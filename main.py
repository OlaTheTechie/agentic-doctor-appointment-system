"""
fastapi main application with multi-agent system
clean, modern implementation with proper error handling and security
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal, List, Any, Dict
import logging
from datetime import datetime
import os
from contextlib import asynccontextmanager

# import the multi-agent system, configuration, and services
from src.agents.multi_agent_system import AppointmentAgent
from src.config.settings import settings
from src.services.message_service import MessageService
from src.api.chat_endpoints import chat_router
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# configure logging
from src.utils.logger import get_logger, log_api_request, log_error
import time

logger = get_logger("app")

# data models
class UserMessage(BaseModel):
    role: Literal["user", "ai", "system"]
    content: str = Field(..., min_length=1, max_length=5000)

class AppointmentDetails(BaseModel):
    patient_name: Optional[str] = Field(None, max_length=100)
    doctor_name: Optional[str] = Field(None, max_length=100)
    specialisation: Optional[str] = Field(None, max_length=50)
    date: Optional[str] = Field(None, pattern=r'^\d{2}-\d{2}-\d{4}$')
    time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    appointment_id: Optional[str] = Field(None, max_length=50)

class UserQuery(BaseModel):
    id_number: int = Field(..., ge=1000000, le=99999999, description="7-8 digit patient ID")
    messages: List[UserMessage] = Field(..., min_items=1, max_items=50)
    intent: Optional[Literal[
        "info_request",
        "book_appointment", 
        "cancel_appointment",
        "reschedule_appointment"
    ]] = "info_request"
    details: Optional[AppointmentDetails] = None
    next: Optional[str] = Field("", max_length=50)
    query: Optional[str] = Field("", max_length=1000)
    current_reasoning: Optional[str] = Field("", max_length=2000)
    step_count: Optional[int] = Field(0, ge=0, le=20)

# application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """handle application startup and shutdown"""
    # startup
    logger.info("starting multi-agent doctor appointment system")
    
    try:
        global agent
        agent = AppointmentAgent()
        logger.info("multi-agent system initialized successfully")
    except Exception as e:
        logger.error(f"failed to initialize multi-agent system: {e}")
        raise
    
    yield
    
    # shutdown
    logger.info("shutting down multi-agent doctor appointment system")

# create fastapi app
app = FastAPI(
    title="Multi-Agent Doctor Appointment System",
    version="3.0.0",
    description="advanced multi-agent appointment management with specialized ai agents",
    lifespan=lifespan
)

# logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """log all api requests with timing"""
    start_time = time.time()
    
    # extract patient id if available
    patient_id = None
    if request.method == "POST":
        try:
            body = await request.body()
            if body:
                import json
                data = json.loads(body)
                patient_id = data.get("id_number") or data.get("patient_id")
        except:
            pass
    
    # process request
    response = await call_next(request)
    
    # calculate duration
    duration = time.time() - start_time
    
    # log the request
    log_api_request(
        method=request.method,
        endpoint=str(request.url.path),
        patient_id=patient_id,
        status_code=response.status_code,
        duration=duration
    )
    
    return response

# cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    max_age=settings.cors.max_age,
)

# initialize services
message_service = MessageService()

# include chat router
app.include_router(chat_router)

# api endpoints
@app.get("/health")
async def health_check():
    """health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "3.0.0",
            "system": "multi-agent",
            "agent_initialized": 'agent' in globals(),
            "data_file_available": os.path.exists(settings.database.data_file_path)
        }
        
        # additional health checks
        if not health_status["agent_initialized"]:
            health_status["status"] = "degraded"
            health_status["warnings"] = ["multi-agent system not initialized"]
        
        if not health_status["data_file_available"]:
            health_status["status"] = "degraded" 
            health_status["warnings"] = health_status.get("warnings", []) + ["data file not found"]
        
        return health_status
        
    except Exception as e:
        logger.error(f"health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="service unhealthy"
        )

@app.post("/execute")
async def execute_multi_agent(request: Request, user_input: UserQuery):
    """
    execute the multi-agent workflow for appointment management
    """
    request_id = f"req_{int(datetime.utcnow().timestamp() * 1000)}"
    
    logger.info(f"processing request {request_id} for patient {user_input.id_number}")
    logger.debug(f"request details: intent={user_input.intent}, messages={len(user_input.messages)}")
    
    try:
        # validate input
        if not user_input.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="at least one message is required"
            )
        
        # check if agent is initialized
        if 'agent' not in globals():
            logger.error("multi-agent system not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="multi-agent system not available"
            )
        
        # convert messages to langchain format
        langchain_messages = message_service.convert_pydantic_to_langchain(user_input.messages)
        
        if not langchain_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="no valid messages provided"
            )
        
        # process with multi-agent system
        try:
            result = agent.process_query(user_input.id_number, langchain_messages)
            
            # extract response data
            response_messages = result.get("messages", [])
            
            # serialize messages for json response
            serialized_messages = message_service.serialize_for_response(response_messages)
            
            # build api response
            api_response = {
                "id_number": user_input.id_number,
                "intent": result.get("current_intent", user_input.intent),
                "details": user_input.details.dict() if user_input.details else None,
                "messages": serialized_messages,
                "next": "FINISH" if result.get("is_complete") else result.get("active_agent", ""),
                "current_reasoning": f"processed by {result.get('active_agent', 'unknown')} agent",
                "request_id": request_id,
                "timestamp": datetime.utcnow(),
                "agent_used": result.get("active_agent"),
                "step_count": result.get("step_count", 0)
            }
            
            logger.info(f"request {request_id} processed successfully by {result.get('active_agent', 'unknown')} agent")
            logger.debug(f"response contains {len(serialized_messages)} messages")
            
            return api_response
            
        except Exception as agent_error:
            log_error("multi_agent_processing", agent_error, {
                "request_id": request_id,
                "patient_id": user_input.id_number,
                "intent": user_input.intent
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="failed to process appointment request with multi-agent system"
            )
        
    except HTTPException:
        # re-raise http exceptions
        raise
    except ValidationError as e:
        logger.warning(f"validation error for {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid input data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"unexpected error for {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="an unexpected error occurred"
        )

@app.get("/agents/status")
async def get_agents_status():
    """get status of all agents in the multi-agent system"""
    try:
        if 'agent' not in globals():
            return {"status": "not_initialized", "agents": []}
        
        return {
            "status": "active",
            "system_version": "3.0.0",
            "agents": [
                {
                    "name": "IntentClassifier",
                    "description": "classifies user intents for proper routing",
                    "status": "active"
                },
                {
                    "name": "AvailabilityAgent", 
                    "description": "handles doctor availability checks",
                    "status": "active"
                },
                {
                    "name": "BookingAgent",
                    "description": "handles appointment booking, canceling, rescheduling",
                    "status": "active"
                },
                {
                    "name": "GeneralAssistantAgent",
                    "description": "handles general inquiries and system information",
                    "status": "active"
                }
            ],
            "workflow_nodes": [
                "classify_intent",
                "availability_agent", 
                "booking_agent",
                "general_agent",
                "finalize_response"
            ]
        }
    except Exception as e:
        logger.error(f"failed to get agents status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to retrieve agents status"
        )

# error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """custom http exception handler"""
    logger.warning(
        f"http exception: {exc.status_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "client_ip": request.client.host
        }
    )
    
    return {
        "error": "HTTP_ERROR",
        "message": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """general exception handler"""
    logger.error(
        f"unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "client_ip": request.client.host
        }
    )
    
    return {
        "error": "INTERNAL_ERROR",
        "message": "an internal error occurred",
        "timestamp": datetime.utcnow()
    }

# development endpoints
if settings.debug:
    @app.get("/debug/workflow")
    async def debug_workflow():
        """debug endpoint to inspect the workflow"""
        if 'agent' not in globals():
            return {"error": "agent not initialized"}
        
        try:
            workflow = agent.workflow()
            return {
                "workflow_type": str(type(workflow)),
                "nodes": list(workflow.nodes.keys()) if hasattr(workflow, 'nodes') else [],
                "debug_mode": True
            }
        except Exception as e:
            return {"error": str(e)}

# run the application
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment (for Render deployment)
    port = int(os.getenv("PORT", settings.api.port))
    host = os.getenv("HOST", settings.api.host)
    
    logger.info(
        f"starting multi-agent doctor appointment system",
        extra={
            "host": host,
            "port": port,
            "debug": settings.debug,
            "environment": "production" if not settings.debug else "development"
        }
    )
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,  # Never reload in production
        access_log=True,
        workers=1  # Single worker for Render compatibility
    )