from pydantic import BaseModel, Field
from typing import List, Optional, Any 


class AgentResponse(BaseModel): 
    next: str = Field(..., examples="booking_node")
    reasoning: Optional[str] = Field(default=None)
    query: Optional[str] = Field(default=None)
    messages: Optional[List[Any]] = Field(default=None)
    id_number: Optional[int] = Field(default=None)
    step_count: Optional[int] = Field(default=None)

class BookingResponse(BaseModel): 
    status: str = Field(..., examples="sucess")
    message: str = Field(..., examples="appointment booked successfully")
    booking_id: Optional[int] = Field(default=None)
    doctor_name: Optional[str] = Field(default=None)
    appointment_date: Optional[str] = Field(default=None)
    appointment_time: Optional[str] = Field(default=None)

