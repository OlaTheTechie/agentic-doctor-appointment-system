"""
api endpoints for memory-powered chat functionality
handles session management and conversation persistence
"""

from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from ..utils.logger import get_logger, log_memory_action, log_error

from ..services.chat_memory_service import (
    chat_memory_service,
    CreateSessionRequest,
    SendMessageRequest,
    ChatMessageResponse,
    SessionResponse
)
from ..services.persistent_chat_service import persistent_storage
try:
    from ..services.message_service import MessageService
    from ..agents.multi_agent_system import AppointmentAgent
    
    # initialize services
    message_service = MessageService()
    appointment_agent = AppointmentAgent()
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some services not available: {e}")
    SERVICES_AVAILABLE = False

# create router
chat_router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# get logger
logger = get_logger("memory")


@chat_router.post("/sessions", response_model=SessionResponse)
async def create_chat_session(request: CreateSessionRequest):
    """create a new chat session for a patient"""
    try:
        logger.info(f"creating new chat session for patient {request.patient_id}")
        
        session = chat_memory_service.create_session(request.patient_id)
        
        log_memory_action(
            action="session_created",
            session_id=session.session_id,
            patient_id=request.patient_id,
            message_count=0
        )
        
        return SessionResponse(
            session_id=session.session_id,
            patient_id=session.patient_id,
            title=session.title,
            created_at=session.created_at,
            is_active=session.is_active,
            message_count=len(session.messages),
            last_activity=None
        )
        
    except Exception as e:
        log_error("chat_session_creation", e, {"patient_id": request.patient_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to create chat session: {str(e)}"
        )


@chat_router.get("/sessions/{patient_id}", response_model=List[SessionResponse])
async def get_patient_sessions(patient_id: int):
    """get all chat sessions for a patient"""
    try:
        if not (1000000 <= patient_id <= 99999999):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid patient id format"
            )
        
        sessions = chat_memory_service.get_patient_sessions(patient_id)
        
        return [
            SessionResponse(
                session_id=session.session_id,
                patient_id=session.patient_id,
                title=session.title,
                created_at=session.created_at,
                is_active=session.is_active,
                message_count=len(session.messages),
                last_activity=session.messages[-1].timestamp if session.messages else None
            )
            for session in sessions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to retrieve sessions: {str(e)}"
        )


@chat_router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(session_id: str, limit: int = 50):
    """get messages from a chat session"""
    try:
        session = chat_memory_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found"
            )
        
        messages = session.get_recent_messages(limit)
        
        return [
            ChatMessageResponse(
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                metadata=msg.metadata
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to retrieve messages: {str(e)}"
        )


@chat_router.post("/sessions/{session_id}/messages")
async def send_message_with_memory(session_id: str, request: SendMessageRequest):
    """send a message in a chat session with memory context"""
    try:
        # validate session exists
        session = chat_memory_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found"
            )
        
        # validate patient id matches session
        if session.patient_id != request.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="patient id does not match session"
            )
        
        # add user message to session
        chat_memory_service.add_message_to_session(
            session_id, "user", request.content, request.metadata
        )
        
        # get conversation context
        context = chat_memory_service.get_session_context(session_id)
        
        # create enhanced query with context
        enhanced_query = request.content
        if context:
            enhanced_query = f"Previous conversation:\n{context}\n\nCurrent question: {request.content}"
        
        # simple response generation (fallback)
        ai_response = f"I understand you're asking: '{request.content}'. "
        
        if SERVICES_AVAILABLE:
            try:
                # prepare messages for multi-agent system
                from langchain_core.messages import HumanMessage, SystemMessage
                
                langchain_messages = []
                if context:
                    langchain_messages.append(SystemMessage(content=f"conversation context: {context}"))
                langchain_messages.append(HumanMessage(content=request.content))
                
                # process with multi-agent system
                result = appointment_agent.process_query(request.patient_id, langchain_messages)
                
                # extract ai response
                if result.get("messages"):
                    response_messages = message_service.serialize_for_response(result["messages"])
                    if response_messages:
                        ai_response = response_messages[-1]["content"]
            except Exception as e:
                ai_response = f"I received your message: '{request.content}'. However, I'm having trouble processing it right now. Please try using the appointment forms above for booking, checking availability, or other requests."
        
        # add ai response to session
        chat_memory_service.add_message_to_session(
            session_id, "assistant", ai_response
        )
        
        # log the memory interaction
        log_memory_action(
            action="message_sent",
            session_id=session_id,
            patient_id=request.patient_id,
            message_count=len(session.messages),
            context_used=bool(context)
        )
        
        logger.info(f"memory chat message processed for session {session_id[:12]}...")
        
        # return enhanced response with session info
        return {
            "session_id": session_id,
            "patient_id": request.patient_id,
            "user_message": request.content,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow(),
            "context_used": bool(context),
            "agent_used": "memory_agent" if SERVICES_AVAILABLE else "simple_agent",
            "is_complete": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to process message: {str(e)}"
        )


@chat_router.get("/sessions/{session_id}/context")
async def get_session_context(session_id: str):
    """get conversation context for a session"""
    try:
        session = chat_memory_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found"
            )
        
        context = session.get_context()
        
        return {
            "session_id": session_id,
            "context": context,
            "message_count": len(session.messages),
            "memory_summary": context[:200] + "..." if len(context) > 200 else context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to get context: {str(e)}"
        )


@chat_router.get("/patients/{patient_id}/preferences")
async def get_patient_preferences(patient_id: int):
    """get extracted preferences from patient's chat history"""
    try:
        if not (1000000 <= patient_id <= 99999999):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid patient id format"
            )
        
        preferences = chat_memory_service.get_patient_preferences(patient_id)
        
        return {
            "patient_id": patient_id,
            "preferences": preferences,
            "extracted_at": datetime.utcnow(),
            "sessions_analyzed": len(chat_memory_service.get_patient_sessions(patient_id))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to extract preferences: {str(e)}"
        )


@chat_router.post("/patients/{patient_id}/search")
async def search_patient_conversations(patient_id: int, query: str):
    """search through patient's conversation history"""
    try:
        if not (1000000 <= patient_id <= 99999999):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid patient id format"
            )
        
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="search query must be at least 2 characters"
            )
        
        matching_messages = chat_memory_service.search_conversations(patient_id, query)
        
        return {
            "patient_id": patient_id,
            "query": query,
            "results": [
                {
                    "session_id": msg.session_id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in matching_messages[:20]  # limit to 20 results
            ],
            "total_matches": len(matching_messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to search conversations: {str(e)}"
        )


@chat_router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str, patient_id: int):
    """delete a chat session"""
    try:
        session = chat_memory_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found"
            )
        
        # verify patient owns the session
        if session.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="not authorized to delete this session"
            )
        
        # mark session as inactive (soft delete)
        session.is_active = False
        
        return {
            "session_id": session_id,
            "deleted": True,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to delete session: {str(e)}"
        )
@chat_router.get("/storage/stats")
async def get_storage_stats():
    """get chat storage statistics"""
    try:
        stats = persistent_storage.get_storage_stats()
        return {
            "storage_stats": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        log_error("storage_stats", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to get storage stats: {str(e)}"
        )