from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Any, Dict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.agents.appointment_agent import AppointmentAgent


app = FastAPI(title="Doctor Appointment Agent API", version="1.0")


class UserMessage(BaseModel):
    role: Literal["user", "ai", "system"]
    content: str


class AppointmentDetails(BaseModel):
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    specialisation: Optional[str] = None
    date: Optional[str] = None  
    time: Optional[str] = None
    appointment_id: Optional[str] = None


class UserQuery(BaseModel):
    id_number: int = Field(..., description="User's unique identification number")
    messages: List[UserMessage] = Field(..., description="List of user/AI messages for context")
    intent: Optional[Literal[
        "info_request",
        "book_appointment",
        "cancel_appointment",
        "reschedule_appointment"
    ]] = "info_request"
    details: Optional[AppointmentDetails] = None
    next: Optional[str] = ""
    query: Optional[str] = ""
    current_reasoning: Optional[str] = ""
    step_count: Optional[int] = 0


def serialize_messages(messages: List[Any]) -> List[Dict[str, Any]]:
    """
    Safely serialize LangChain message objects to dicts for JSON response.
    """
    serialized = []
    for msg in messages:
        if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
            serialized.append({
                "role": msg.type,
                "content": msg.content,
                "name": getattr(msg, "name", None),
            })
        elif isinstance(msg, dict):
            serialized.append(msg)
        else:
            serialized.append({"role": "unknown", "content": str(msg)})
    return serialized


agent = AppointmentAgent()


@app.post("/execute")
def execute_agent(user_input: UserQuery):
    """
    Endpoint to run the AppointmentAgent workflow.
    Handles all intents (info, booking, cancellation, etc.)
    """
    # initialize workflow graph aplication
    app_graph = agent.workflow()

    # convert pydantic messages into LangChain message objects
    input_messages = []
    for msg in user_input.messages:
        if msg.role == "user":
            input_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "ai":
            input_messages.append(AIMessage(content=msg.content))
        elif msg.role == "system":
            input_messages.append(SystemMessage(content=msg.content))

    # prepare agent state exactly as expected by the agent
    query_data = {
        "messages": input_messages,
        "id_number": user_input.id_number,
        "next": user_input.next,
        "query": user_input.query,
        "current_reasoning": user_input.current_reasoning,
        "step_count": user_input.step_count,
    }

    # invoke agent workflow with the query
    response = app_graph.invoke(query_data, config={"recursion_limit": 20})

    # serialize messages for JSON response
    serialized_messages = serialize_messages(response.get("messages", []))

    return {
        "id_number": user_input.id_number,
        "intent": user_input.intent,
        "details": user_input.details.dict() if user_input.details else None,
        "messages": serialized_messages,
        "next": response.get("next", None),
        "current_reasoning": response.get("current_reasoning", None),
    }
