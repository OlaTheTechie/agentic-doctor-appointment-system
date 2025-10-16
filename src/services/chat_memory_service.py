"""
memory-powered chat service for persistent conversations
handles conversation storage, retrieval, and intelligent memory management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from pydantic import BaseModel, Field

from ..utils.llm import LLM
from .persistent_chat_service import (
    persistent_storage, 
    PersistentChatSession, 
    PersistentChatMessage
)


@dataclass
class ChatMessage:
    """chat message data structure"""
    session_id: str
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None


class ChatSession:
    """represents a chat session with memory"""
    
    def __init__(self, patient_id: int, session_id: Optional[str] = None):
        self.patient_id = patient_id
        self.session_id = session_id or self._generate_session_id()
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.title = "new conversation"
        
        # initialize simple memory buffer
        self.memory_buffer = []
        self.max_messages = 20  # keep last 20 messages in memory
    
    def _generate_session_id(self) -> str:
        """generate unique session id"""
        timestamp = int(datetime.utcnow().timestamp())
        return f"chat_{self.patient_id}_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """add message to session"""
        message = ChatMessage(
            session_id=self.session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.messages.append(message)
        
        # update simple memory buffer
        self.memory_buffer.append({"role": role, "content": content})
        
        # keep only recent messages in memory
        if len(self.memory_buffer) > self.max_messages:
            self.memory_buffer = self.memory_buffer[-self.max_messages:]
        
        # auto-generate title from first user message
        if role == "user" and self.title == "new conversation":
            self.title = self._generate_title(content)
        
        # save message to persistent storage
        persistent_message = PersistentChatMessage(
            session_id=self.session_id,
            role=role,
            content=content,
            timestamp=message.timestamp.isoformat(),
            metadata=metadata
        )
        persistent_storage.save_message(persistent_message)
    
    def _generate_title(self, first_message: str) -> str:
        """generate conversation title from first message"""
        # simple title generation - can be enhanced with llm
        words = first_message.split()[:5]
        return " ".join(words) + ("..." if len(first_message.split()) > 5 else "")
    
    def get_context(self) -> str:
        """get conversation context for current query"""
        if not self.memory_buffer:
            return ""
        
        # create simple context from recent messages
        context_parts = []
        for msg in self.memory_buffer[-10:]:  # last 10 messages
            role = "Patient" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def get_recent_messages(self, count: int = 10) -> List[ChatMessage]:
        """get recent messages from session"""
        return self.messages[-count:] if self.messages else []
    
    def to_dict(self) -> Dict:
        """convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "patient_id": self.patient_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "message_count": len(self.messages),
            "last_activity": self.messages[-1].timestamp.isoformat() if self.messages else None
        }


class ChatMemoryService:
    """service for managing chat sessions and memory with persistent storage"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}  # in-memory cache
        self.patient_sessions: Dict[int, List[str]] = {}  # in-memory cache
    
    def create_session(self, patient_id: int) -> ChatSession:
        """create new chat session"""
        session = ChatSession(patient_id)
        
        # store session in memory cache
        self.sessions[session.session_id] = session
        
        # track patient sessions in memory
        if patient_id not in self.patient_sessions:
            self.patient_sessions[patient_id] = []
        self.patient_sessions[patient_id].append(session.session_id)
        
        # save session to persistent storage
        persistent_session = PersistentChatSession(
            session_id=session.session_id,
            patient_id=session.patient_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.created_at.isoformat(),
            is_active=session.is_active,
            message_count=0
        )
        persistent_storage.save_session(persistent_session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """get existing session (load from persistent storage if needed)"""
        # check memory cache first
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # load from persistent storage
        persistent_session = persistent_storage.get_session(session_id)
        if not persistent_session:
            return None
        
        # create session object and load into memory
        session = ChatSession(persistent_session.patient_id)
        session.session_id = persistent_session.session_id
        session.title = persistent_session.title
        session.created_at = datetime.fromisoformat(persistent_session.created_at)
        session.is_active = persistent_session.is_active
        
        # load messages
        persistent_messages = persistent_storage.get_session_messages(session_id)
        for p_msg in persistent_messages:
            msg = ChatMessage(
                session_id=p_msg.session_id,
                role=p_msg.role,
                content=p_msg.content,
                timestamp=datetime.fromisoformat(p_msg.timestamp),
                metadata=p_msg.metadata
            )
            session.messages.append(msg)
            session.memory_buffer.append({"role": p_msg.role, "content": p_msg.content})
        
        # cache in memory
        self.sessions[session_id] = session
        return session
    
    def get_patient_sessions(self, patient_id: int) -> List[ChatSession]:
        """get all sessions for a patient (from persistent storage)"""
        # get from persistent storage
        persistent_sessions = persistent_storage.get_patient_sessions(patient_id)
        
        sessions = []
        for p_session in persistent_sessions:
            # check if already in memory cache
            if p_session.session_id in self.sessions:
                sessions.append(self.sessions[p_session.session_id])
            else:
                # load session into memory cache
                session = ChatSession(p_session.patient_id)
                session.session_id = p_session.session_id
                session.title = p_session.title
                session.created_at = datetime.fromisoformat(p_session.created_at)
                session.is_active = p_session.is_active
                
                # load messages from persistent storage
                persistent_messages = persistent_storage.get_session_messages(p_session.session_id)
                for p_msg in persistent_messages:
                    msg = ChatMessage(
                        session_id=p_msg.session_id,
                        role=p_msg.role,
                        content=p_msg.content,
                        timestamp=datetime.fromisoformat(p_msg.timestamp),
                        metadata=p_msg.metadata
                    )
                    session.messages.append(msg)
                    session.memory_buffer.append({"role": p_msg.role, "content": p_msg.content})
                
                # cache in memory
                self.sessions[session.session_id] = session
                sessions.append(session)
        
        return sessions
    
    def add_message_to_session(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """add message to existing session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.add_message(role, content, metadata)
        return True
    
    def get_session_context(self, session_id: str) -> str:
        """get conversation context for session"""
        session = self.get_session(session_id)
        return session.get_context() if session else ""
    
    def search_conversations(self, patient_id: int, query: str) -> List[ChatMessage]:
        """search through patient's conversation history"""
        sessions = self.get_patient_sessions(patient_id)
        matching_messages = []
        
        query_lower = query.lower()
        
        for session in sessions:
            for message in session.messages:
                if query_lower in message.content.lower():
                    matching_messages.append(message)
        
        return matching_messages
    
    def get_patient_preferences(self, patient_id: int) -> Dict:
        """extract patient preferences from conversation history"""
        sessions = self.get_patient_sessions(patient_id)
        
        # collect all user messages
        user_messages = []
        for session in sessions:
            user_messages.extend([
                msg.content for msg in session.messages 
                if msg.role == "user"
            ])
        
        # analyze for preferences (simplified version)
        preferences = {
            "preferred_times": [],
            "preferred_doctors": [],
            "communication_style": "standard",
            "special_requirements": []
        }
        
        # simple keyword-based extraction
        all_text = " ".join(user_messages).lower()
        
        # time preferences
        if "morning" in all_text:
            preferences["preferred_times"].append("morning")
        if "afternoon" in all_text:
            preferences["preferred_times"].append("afternoon")
        if "evening" in all_text:
            preferences["preferred_times"].append("evening")
        
        return preferences
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """cleanup sessions older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if session.created_at < cutoff_date and not session.is_active:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            session = self.sessions.pop(session_id)
            # remove from patient sessions
            if session.patient_id in self.patient_sessions:
                self.patient_sessions[session.patient_id].remove(session_id)


# global service instance
chat_memory_service = ChatMemoryService()


# api request/response models
class CreateSessionRequest(BaseModel):
    patient_id: int = Field(..., ge=1000000, le=99999999)


class SendMessageRequest(BaseModel):
    session_id: str
    patient_id: int = Field(..., ge=1000000, le=99999999)
    content: str = Field(..., min_length=1, max_length=5000)
    metadata: Optional[Dict] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None


class SessionResponse(BaseModel):
    session_id: str
    patient_id: int
    title: str
    created_at: datetime
    is_active: bool
    message_count: int
    last_activity: Optional[datetime] = None