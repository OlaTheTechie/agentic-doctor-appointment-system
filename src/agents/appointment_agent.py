from typing import Literal, List, Any
from langchain_core.tools import tool
from langgraph.types import Command
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.prompts.prompt import system_prompt
from src.utils.llm import LLM
from src.toolkit.appointment_tools import (
    cancel_appointment,
    set_appointment,
    reschedule_appointment
)
from src.toolkit.availability_tools import (
    check_availability_by_doctor,
    check_availability_by_specialisation
)
from src.utils.agent_states import Router, AgentState


class AppointmentAgent:
    def __init__(self):
        llm_instance = LLM()
        self.llm = llm_instance.get_model()

    

    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Literal
from langgraph.graph import Command, END

def supervisor_node(self, state: AgentState) -> Command[
    Literal["information_node", "booking_node", "__end__"]
]:
    print("========below is my state after entering========")
    print(state)

    state["step_count"] = state.get("step_count", 0) + 1

    if state["step_count"] > 10:
        print("Maximum step count reached. Ending conversation.")
        return Command(goto=END, update={"next": "FINISH"})

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
        else:
            converted_messages.append(msg)
    state["messages"] = converted_messages

    if len(state["messages"]) >= 2:
        last_name = getattr(state["messages"][-1], "name", "")
        prev_name = getattr(state["messages"][-2], "name", "")
        if last_name == prev_name:
            print("Repeated routing detected. Ending conversation.")
            return Command(goto=END, update={"next": "FINISH"})

    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the following workers. "
        "### SPECIALIZED ASSISTANT: \n"
        "WORKER: information_agent \nDESCRIPTION: Handles FAQs about hospital services and checks doctor availability. \n\n"
        "WORKER: booking_agent \nDESCRIPTION: Handles appointment actions only (book, cancel, reschedule). \n\n"
        "WORKER: FINISH \nDESCRIPTION: Use this once the user's query is fully resolved or no further action is required.\n\n"
        "Rules: Do not answer directly. Route queries correctly. Finish if query is resolved or step count is high."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"user's identification number is {state['id_number']}")
    ] + state["messages"]

    print("========this is the message============")
    print(messages)

    query = ""
    if len(state["messages"]) == 1:
        query = getattr(state["messages"][0], "content", "")

    print("======below is my query=======")
    print(query)

    response = self.llm.with_structured_output(Router).invoke(messages)
    goto = response.get("next", "FINISH")

    print("========this is where i am routing to next======")
    print(goto)

    if goto == "FINISH":
        print("Supervisor decided to finish the conversation.")
        return Command(goto=END, update={"next": "FINISH"})

    if state["messages"]:
        last_content = getattr(state["messages"][-1], "content", "").lower()
        if any(phrase in last_content for phrase in [
            "no available appointments",
            "no availability",
            "unable to proceed",
            "cannot continue"
        ]):
            print("Detected unresolved dead-end. Finishing conversation.")
            return Command(goto=END, update={"next": "FINISH"})

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

        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_prompt),
            ("placeholder", "{messages}")
        ])

        information_agent = create_react_agent(
            model=self.llm,
            tools=[check_availability_by_doctor, check_availability_by_specialisation]
        )

        
        result = information_agent.invoke(state)
        state["step_count"] += 1

        if state["step_count"] > 10:
            state["next"] = "FINISH"

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="information_node")
                ]
            },
            goto="supervisor"
        )

    def booking_node(self, state: AgentState) -> Command[Literal["supervisor"]]:
        print("==========calling the booking node=============")

        sys_prompt = (
            "You are a specialized agent to set, cancel, or reschedule appointments. "
            "You have access to the tools.\n"
            "Always ask politely if you need additional information to execute the tool.\n"
            "Consider the current year as 2025."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_prompt),
            ("placeholder", "{messages}")
        ])

        booking_agent = create_react_agent(
            model=self.llm,
            tools=[set_appointment, cancel_appointment, reschedule_appointment]
        )

        result = booking_agent.invoke(state)

        state["step_count"] += 1

        if state["step_count"] > 10:
            state["next"] = "FINISH"

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="booking_node")
                ]
            },
            goto="supervisor"
        )

    def workflow(self):
        self.graph = StateGraph(AgentState)
        self.graph.add_node("supervisor", self.supervisor_node)
        self.graph.add_node("information_node", self.information_node)
        self.graph.add_node("booking_node", self.booking_node)
        self.graph.add_edge(START, "supervisor")
        self.app = self.graph.compile()
        return self.app
