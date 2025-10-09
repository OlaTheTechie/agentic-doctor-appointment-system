# from fastapi import APIRouter, HTTPException
# from app.models.request_model import AgentStateRequest, Message, BookingRequest, AgentRequest
# from app.models.response_models import AgentResponse, BookingResponse

# from src.agents.appointment_agent import AppointmentAgent

# router = APIRouter(
#     prefix="/agent", 
#     tags=["Agent"]
# )

# agent = AppointmentAgent()

# @router.post("/supervisor", response_model=AgentResponse)
# async def supervisor_route(request: AgentResponse): 
#     """
#     Supervisor node endpoint.
#     Receives the current state and routes to the next node.
#     """

#     try: 
#         state = request.dict()
#         command = agent.supervisor_node()

#         response = AgentResponse(
#             next=command.goto,
#             reasoning=state.get("current_reasoning"), 
#             query=state.get("query"), 
#             messages=[
#                 Message(role=msg.rolde, content=msg.content) for msg in state["messages"]
#             ], 
#         )

#         return response
    
#     except Exception as e: 
#         raise HTTPException(
#             status_code=500, 
#             detail=str(e)
#         )
    
# @router.post("/information", response_model=AgentResponse)
# async def information_route(request: AgentResponse): 
#     """
#     Information node endpoint.
#     Handles the general questions or date retrieval logic.
#     """

#     try: 
#         state = request.dict()
#         command = agent.information_node(state)

#         response = AgentResponse(
#             next=command.goto, 
#             reasoning=state.get("current_reasoning"), 
#             query=state.get("query"), 
#             messages=[
#                 Message(role=msg.role, content=msg.content) for msg in state["messages"]
#             ],
#         )

#         return response 
#     except Exception as e: 
#         raise HTTPException(
#             status_code=500, 
#             detail=str(e)
#         )
    

# @router.post("/booking", response_model=AgentResponse)
# async def booking_route(request: AgentRequest): 
#     """
#     Booking node endpoint.
#     Handles doctor appointment bookings.
#     """

#     try: 
#         state = request.dict()
#         command = agent.booking_node(state)

#         response = AgentResponse(
#             next=command.goto, 
#             reasoning=state.get("current_reasoning"), 
#             query=state.get("query"), 
#             messages=[
#                 Message(
#                     role=msg.role, 
#                     content=msg.content
#                 ) for msg in state["messages"]
#             ],
#         )

#         return response
#     except Exception as e: 
#         raise HTTPException(
#             status_code=500, 
#             detail=str(e)
#         )


from fastapi import APIRouter, HTTPException
from app.models.request_models import AgentStateRequest, BookingRequest, AgentRequest, Message
from app.models.response_models import AgentResponse, BookingResponse
from src.agents.appointment_agent import AppointmentAgent

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)

agent = AppointmentAgent()

# ==============================
# SUPERVISOR NODE
# ==============================
@router.post("/supervisor", response_model=AgentResponse)
async def supervisor_route(request: AgentStateRequest):
    """
    Supervisor node endpoint.
    Receives the current state and routes to the next node.
    """
    try:
        state = request.dict()
        command = agent.supervisor_node(state)

        response = AgentResponse(
            next=command.goto,
            reasoning=state.get("current_reasoning"),
            query=state.get("query"),
            messages=[
                Message(role=msg["role"], content=msg["content"])
                for msg in state["messages"]
            ],
            id_number=state.get("id_number"),
            step_count=state.get("step_count"),
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# BOOKING NODE
# ==============================
@router.post("/booking", response_model=BookingResponse)
async def booking_route(request: BookingRequest):
    """
    Booking node endpoint.
    Handles doctor appointment bookings.
    """
    try:
        booking = agent.booking_node(request.dict())

        response = BookingResponse(
            status="success",
            message="Appointment booked successfully",
            booking_id=booking.get("booking_id"),
            doctor_name=request.doctor_name,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
