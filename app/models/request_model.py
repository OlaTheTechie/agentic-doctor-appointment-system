from pydantic import BaseModel, Field
from typing import List, Optional, Any 


class Message(BaseModel): 
    role: str = Field(..., examples="user")
    content: str = Field(..., examples="I want to book an appointment")

class AgentStateRequest(BaseModel): 
    id_number: int = Field(..., examples=12345678)
    messages: List[Message] = Field(default_factory=list)
    next: Optional[str] = Field(default="")
    query: Optional[str] = Field(default="")
    current_reasoning: Optional[str] = Field(default="")
    step_count: str = Field(default=0)

class BookingRequest(BaseModel): 
    id_number: int = Field(..., examples=12345678)
    doctor_name: str = Field(..., examples="Dr. Kevin Anderson")
    appointment_date: str = Field(..., examples="12-10-2025")
    appointment_time: str = Field(..., examples="10:20 AM")

class AgentRequest(BaseModel):
    id_number: int
    messages: List[Message]
    next: Optional[str] = None
    query: Optional[str] = None
    current_reasoning: Optional[str] = None
