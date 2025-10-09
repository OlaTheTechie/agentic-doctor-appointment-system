from typing import Literal, List, Any
from langchain_core.tools import tool
from langgraph.types import Command
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
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

    # def supervisor_node(self, state: AgentState) -> Command[
    #     Literal["information_node", "booking_node", "__end__"]
    # ]:
    #     print("========below is my state after entering========")
    #     print(state)

    #     messages = [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": f"user's identification number is {state['id_number']}"}
    #     ] + state["messages"]

    #     print("========this is the message============")
    #     print(messages)

    #     query = ""
    #     if len(state["messages"]) == 1:
    #         query = state["messages"][0].content

    #     print("======below is my query=======")
    #     print(query)

    #     response = self.llm.with_structured_output(Router).invoke(messages)
    #     goto = response["next"]

    #     print("========this is where i am routing to next======")
    #     print(goto)

    #     if goto == "FINISH":
    #         goto = END

    #     if query:
    #         return Command(
    #             goto=goto,
    #             update={
    #                 "next": goto,
    #                 "query": query,
    #                 "current_reasoning": response["reasoning"],
    #                 "messages": [
    #                     HumanMessage(
    #                         content=f"user's identification number is {state['id_number']}"
    #                     )
    #                 ]
    #             }
    #         )

    #     return Command(
    #         goto=goto,
    #         update={
    #             "next": goto,
    #             "current_reasoning": response["reasoning"]
    #         }
    #     )


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

        # detect repeated routing (same agent twice in a row)
        if len(state["messages"]) >= 2:
            last_name = getattr(state["messages"][-1], "name", "")
            prev_name = getattr(state["messages"][-2], "name", "")
            if last_name == prev_name:
                print("Repeated routing detected. Ending conversation.")
                return Command(goto=END, update={"next": "FINISH"})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"user's identification number is {state['id_number']}"}
        ] + state["messages"]

        print("========this is the message============")
        print(messages)

        query = ""
        if len(state["messages"]) == 1:
            query = state["messages"][0].content

        print("======below is my query=======")
        print(query)

        response = self.llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]

        print("========this is where i am routing to next======")
        print(goto)

        # terminate if LLM signals finish
        if goto == "FINISH":
            print("Supervisor decided to finish the conversation.")
            return Command(goto=END, update={"next": "FINISH"})

        # detect no progress / dead end
        if state["messages"]:
            last_content = state["messages"][-1].content.lower()
            if any(phrase in last_content for phrase in [
                "no available appointments",
                "no availability",
                "unable to proceed",
                "cannot continue"
            ]):
                print("Detected unresolved dead-end. Finishing conversation.")
                return Command(goto=END, update={"next": "FINISH"})

        # continue routing normally
        if query:
            return Command(
                goto=goto,
                update={
                    "next": goto,
                    "query": query,
                    "current_reasoning": response["reasoning"],
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
                "current_reasoning": response["reasoning"]
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
