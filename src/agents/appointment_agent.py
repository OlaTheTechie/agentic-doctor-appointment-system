from typing import Literal, List, Any, Dict
from langchain_core.tools import tool
from langgraph.graph.state import Command, END  # Command & END live here in current langgraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.prompts.prompt import system_prompt
from src.utils.llm import LLM
from src.toolkit.appointment_tools import (
    cancel_appointment,
    set_appointment,
    reschedule_appointment,
)
from src.toolkit.availability_tools import (
    check_availability_by_doctor,
    check_availability_by_specialisation,
)
from src.utils.agent_states import Router, AgentState


class AppointmentAgent:
    def __init__(self):
        llm_instance = LLM()
        self.llm = llm_instance.get_model()

    def _convert_incoming_messages(
        self, incoming: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        Convert list of dict messages (from API) into message objects (HumanMessage/AIMessage/SystemMessage).
        Also accept already-converted message objects and return them unchanged.
        """
        out = []
        for msg in incoming or []:
            if isinstance(msg, dict):
                role = (msg.get("role") or "").lower()
                content = msg.get("content", "")
                if role == "user":
                    out.append(HumanMessage(content=content))
                elif role in ("assistant", "ai", "bot"):
                    out.append(AIMessage(content=content))
                elif role == "system":
                    out.append(SystemMessage(content=content))
                else:
                    # unknown role  treat as human by default
                    out.append(HumanMessage(content=content))
            else:
                # assume already a message object (HumanMessage/AIMessage/SystemMessage)
                out.append(msg)
        return out

    def _serializable_messages(self, messages: List[Any]) -> List[Dict[str, str]]:
        """
        Convert message objects (or dict-like) to simple dicts suitable for LLM calls:
        [{"role": "...", "content": "..."}]
        """
        out = []
        for m in messages or []:
            if isinstance(m, dict):
                role = m.get("role", "user")
                content = m.get("content", "")
            else:
                # message objects from langchain_core.messages have `__class__.__name__` and `.content`
                role = getattr(m, "role", None)
                if not role:
                    # try map class name
                    cls_name = m.__class__.__name__.lower()
                    if "human" in cls_name:
                        role = "user"
                    elif "ai" in cls_name or "assistant" in cls_name:
                        role = "assistant"
                    elif "system" in cls_name:
                        role = "system"
                    else:
                        role = "user"
                content = getattr(m, "content", "")
            out.append({"role": role, "content": content})
        return out

    def supervisor_node(self, state: AgentState) -> Command[
        Literal["information_node", "booking_node", "__end__"]
    ]:
        print("========below is my state after entering========")
        print(state)

        # increment step count
        state["step_count"] = state.get("step_count", 0) + 1

        # termination condition: too many steps
        if state["step_count"] > 10:
            print("Maximum step count reached. Ending conversation.")
            return Command(goto=END, update={"next": "FINISH"})

        # convert messages from dicts → LangChain message objects
        converted_messages = []
        for msg in state.get("messages", []):
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    converted_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    converted_messages.append(AIMessage(content=content))
                elif role == "system":
                    converted_messages.append(SystemMessage(content=content))
            elif isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                converted_messages.append(msg)
            else:
                print(f"Skipping unknown message type: {msg}")
        state["messages"] = converted_messages

        # detect repeated routing
        if len(state["messages"]) >= 2:
            last_name = getattr(state["messages"][-1], "name", "")
            prev_name = getattr(state["messages"][-2], "name", "")
            if last_name == prev_name:
                print("Repeated routing detected. Ending conversation.")
                return Command(goto=END, update={"next": "FINISH"})

        # build full message context
        system_message = SystemMessage(content=system_prompt)
        user_identity = HumanMessage(content=f"user's identification number is {state['id_number']}")
        messages = [system_message, user_identity] + state["messages"]

        print("========this is the message============")
        print(messages)

        # safely extract query
        query = ""
        if len(state["messages"]) == 1 and hasattr(state["messages"][0], "content"):
            query = state["messages"][0].content

        print("======below is my query=======")
        print(query)

        # invoke model
        response = self.llm.with_structured_output(Router).invoke(messages)
        goto = response.get("next", "FINISH")

        print("========this is where i am routing to next======")
        print(goto)

        # end if model signals finish
        if goto == "FINISH":
            print("Supervisor decided to finish the conversation.")
            return Command(goto=END, update={"next": "FINISH"})

        # detect dead ends
        if state["messages"]:
            last_msg = state["messages"][-1]
            last_content = getattr(last_msg, "content", "").lower()
            if any(phrase in last_content for phrase in [
                "no available appointments",
                "no availability",
                "unable to proceed",
                "cannot continue"
            ]):
                print("Detected unresolved dead-end. Finishing conversation.")
                return Command(goto=END, update={"next": "FINISH"})

        # route normally
        if query:
            return Command(
                goto=goto,
                update={
                    "next": goto,
                    "query": query,
                    "current_reasoning": response.get("reasoning", ""),
                    "messages": [
                        HumanMessage(
                            content=f"user's identification number is {state['id_number']}"
                        )
                    ]
                }
            )

        return Command(
            goto=goto,
            update={
                "next": goto,
                "current_reasoning": response.get("reasoning", "")
            }
        )

    def information_node(self, state: AgentState) -> Command[Literal["supervisor"]]:
        print("========agent has called the information node=======")

        sys_prompt = (
            "You are a specialized agent that provides information related to doctor availability "
            "or hospital FAQs. You have access to the tools.\n"
            "Always ask politely if you need additional information to execute the tool.\n"
            "Consider the current year as 2025."
        )

        # convert incoming messages and produce serializable form
        state["messages"] = self._convert_incoming_messages(state.get("messages", []))
        serial_messages = self._serializable_messages(state["messages"])

        information_agent = create_react_agent(
            model=self.llm,
            tools=[check_availability_by_doctor, check_availability_by_specialisation],
        )

        # prepare input for the react agent: many executors expect a dict with messages
        react_input = {"messages": serial_messages, "id_number": state.get("id_number")}

        try:
            result = information_agent.invoke(react_input)
        except Exception as e:
            print("Information agent call failed:", str(e))
            # mark finish on failure
            return Command(goto=END, update={"next": "FINISH"})

        # increment step count and check termination
        state["step_count"] = int(state.get("step_count", 0)) + 1
        if state["step_count"] > 10:
            return Command(goto=END, update={"next": "FINISH"})

        # extract last assistant message from result safely
        try:
            last_msg_content = result["messages"][-1].content if result.get("messages") else ""
        except Exception:
            last_msg_content = str(result)

        # append assistant message object to state.messages (for later checks)
        state["messages"] = state.get("messages", []) + [AIMessage(content=last_msg_content, name="information_node")]

        return Command(
            goto="supervisor",
            update={
                "messages": self._serializable_messages(state["messages"]),
                "current_reasoning": state.get("current_reasoning", ""),
                "step_count": state.get("step_count", 0),
            },
        )

    def booking_node(self, state: AgentState) -> Command[Literal["supervisor"]]:
        print("==========calling the booking node=============")

        sys_prompt = (
            "You are a specialized agent to set, cancel, or reschedule appointments. "
            "You have access to the tools.\n"
            "Always ask politely if you need additional information to execute the tool.\n"
            "Consider the current year as 2025."
        )

        # convert and serialize
        state["messages"] = self._convert_incoming_messages(state.get("messages", []))
        serial_messages = self._serializable_messages(state["messages"])

        booking_agent = create_react_agent(
            model=self.llm,
            tools=[set_appointment, cancel_appointment, reschedule_appointment],
        )

        react_input = {"messages": serial_messages, "id_number": state.get("id_number")}

        try:
            result = booking_agent.invoke(react_input)
        except Exception as e:
            print("Booking agent call failed:", str(e))
            return Command(goto=END, update={"next": "FINISH"})

        state["step_count"] = int(state.get("step_count", 0)) + 1
        if state["step_count"] > 10:
            return Command(goto=END, update={"next": "FINISH"})

        # extract response body safely
        try:
            last_msg_content = result["messages"][-1].content if result.get("messages") else ""
        except Exception:
            last_msg_content = str(result)

        state["messages"] = state.get("messages", []) + [AIMessage(content=last_msg_content, name="booking_node")]

        return Command(
            goto="supervisor",
            update={
                "messages": self._serializable_messages(state["messages"]),
                "current_reasoning": state.get("current_reasoning", ""),
                "step_count": state.get("step_count", 0),
            },
        )

    def workflow(self):
        self.graph = StateGraph(AgentState)
        self.graph.add_node("supervisor", self.supervisor_node)
        self.graph.add_node("information_node", self.information_node)
        self.graph.add_node("booking_node", self.booking_node)
        self.graph.add_edge(START, "supervisor")
        self.app = self.graph.compile()
        return self.app
