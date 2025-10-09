from pydantic import BaseModel, Field
from typing import List, Optional, Any


class Message(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="I want to book an appointment")


class AgentStateRequest(BaseModel):
    id_number: int = Field(..., example=12345678)
    messages: List[Message] = Field(default_factory=list)
    next: Optional[str] = Field(default="")
    query: Optional[str] = Field(default="")
    current_reasoning: Optional[str] = Field(default="")
    step_count: int = Field(default=0)

    model_config = {"arbitrary_types_allowed": True}


class BookingRequest(BaseModel):
    id_number: int = Field(..., example=12345678)
    doctor_name: str = Field(..., example="Dr. Kevin Anderson")
    appointment_date: str = Field(..., example="12-10-2025")
    appointment_time: str = Field(..., example="10:20 AM")

    model_config = {"arbitrary_types_allowed": True}


class AgentRequest(BaseModel):
    id_number: int
    messages: List[Message]
    next: Optional[str] = None
    query: Optional[str] = None
    current_reasoning: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}
