"""
persistent chat storage service
saves chat messages and sessions to files for persistence across server restarts
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid

from ..utils.logger import get_logger

logger = get_logger("memory")


@dataclass
class PersistentChatMessage:
    """persistent chat message structure"""
    session_id: str
    role: str  # user, assistant, system
    content: str
    timestamp: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PersistentChatMessage':
        return cls(**data)


@dataclass
class PersistentChatSession:
    """persistent chat session structure"""
    session_id: str
    patient_id: int
    title: str
    created_at: str
    updated_at: str
    is_active: bool
    message_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PersistentChatSession':
        return cls(**data)


class PersistentChatStorage:
    """handles persistent storage of chat sessions and messages"""
    
    def __init__(self, storage_dir: str = "data/chat_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # storage files
        self.sessions_file = self.storage_dir / "sessions.json"
        self.messages_file = self.storage_dir / "messages.json"
        self.patient_index_file = self.storage_dir / "patient_index.json"
        
        # ensure files exist
        self._ensure_files_exist()
        
        logger.info(f"persistent chat storage initialized at {self.storage_dir}")
    
    def _ensure_files_exist(self):
        """ensure storage files exist with empty data"""
        if not self.sessions_file.exists():
            self._write_json(self.sessions_file, {})
        
        if not self.messages_file.exists():
            self._write_json(self.messages_file, {})
        
        if not self.patient_index_file.exists():
            self._write_json(self.patient_index_file, {})
    
    def _read_json(self, file_path: Path) -> Dict:
        """safely read json file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"error reading {file_path}: {e}")
            return {}
    
    def _write_json(self, file_path: Path, data: Dict):
        """safely write json file"""
        try:
            # write to temp file first, then rename (atomic operation)
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # atomic rename
            temp_file.rename(file_path)
            
        except Exception as e:
            logger.error(f"error writing {file_path}: {e}")
            raise
    
    def save_session(self, session: PersistentChatSession):
        """save or update a chat session"""
        sessions = self._read_json(self.sessions_file)
        sessions[session.session_id] = session.to_dict()
        self._write_json(self.sessions_file, sessions)
        
        # update patient index
        patient_index = self._read_json(self.patient_index_file)
        patient_id_str = str(session.patient_id)
        
        if patient_id_str not in patient_index:
            patient_index[patient_id_str] = []
        
        if session.session_id not in patient_index[patient_id_str]:
            patient_index[patient_id_str].append(session.session_id)
        
        self._write_json(self.patient_index_file, patient_index)
        
        logger.debug(f"saved session {session.session_id[:12]}... for patient {session.patient_id}")
    
    def get_session(self, session_id: str) -> Optional[PersistentChatSession]:
        """get a chat session by id"""
        sessions = self._read_json(self.sessions_file)
        session_data = sessions.get(session_id)
        
        if session_data:
            return PersistentChatSession.from_dict(session_data)
        return None
    
    def get_patient_sessions(self, patient_id: int) -> List[PersistentChatSession]:
        """get all sessions for a patient"""
        patient_index = self._read_json(self.patient_index_file)
        session_ids = patient_index.get(str(patient_id), [])
        
        sessions = []
        sessions_data = self._read_json(self.sessions_file)
        
        for session_id in session_ids:
            if session_id in sessions_data:
                sessions.append(PersistentChatSession.from_dict(sessions_data[session_id]))
        
        # sort by created_at (newest first)
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions
    
    def save_message(self, message: PersistentChatMessage):
        """save a chat message"""
        messages = self._read_json(self.messages_file)
        
        # use session_id as key, store list of messages
        if message.session_id not in messages:
            messages[message.session_id] = []
        
        messages[message.session_id].append(message.to_dict())
        self._write_json(self.messages_file, messages)
        
        # update session message count
        session = self.get_session(message.session_id)
        if session:
            session.message_count = len(messages[message.session_id])
            session.updated_at = datetime.utcnow().isoformat()
            self.save_session(session)
        
        logger.debug(f"saved message to session {message.session_id[:12]}...")
    
    def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> List[PersistentChatMessage]:
        """get messages for a session"""
        messages = self._read_json(self.messages_file)
        session_messages = messages.get(session_id, [])
        
        # convert to objects
        message_objects = [PersistentChatMessage.from_dict(msg) for msg in session_messages]
        
        # apply limit if specified
        if limit:
            message_objects = message_objects[-limit:]
        
        return message_objects
    
    def delete_session(self, session_id: str, patient_id: int):
        """delete a session and its messages"""
        # mark session as inactive
        session = self.get_session(session_id)
        if session:
            session.is_active = False
            self.save_session(session)
        
        # optionally delete messages (or keep for audit)
        # messages = self._read_json(self.messages_file)
        # if session_id in messages:
        #     del messages[session_id]
        #     self._write_json(self.messages_file, messages)
        
        logger.info(f"deleted session {session_id[:12]}... for patient {patient_id}")
    
    def search_messages(self, patient_id: int, query: str, limit: int = 20) -> List[PersistentChatMessage]:
        """search messages for a patient"""
        patient_sessions = self.get_patient_sessions(patient_id)
        matching_messages = []
        
        query_lower = query.lower()
        
        for session in patient_sessions:
            session_messages = self.get_session_messages(session.session_id)
            
            for message in session_messages:
                if query_lower in message.content.lower():
                    matching_messages.append(message)
                    
                    if len(matching_messages) >= limit:
                        break
            
            if len(matching_messages) >= limit:
                break
        
        return matching_messages
    
    def get_storage_stats(self) -> Dict:
        """get storage statistics"""
        sessions = self._read_json(self.sessions_file)
        messages = self._read_json(self.messages_file)
        patient_index = self._read_json(self.patient_index_file)
        
        total_messages = sum(len(msgs) for msgs in messages.values())
        active_sessions = sum(1 for s in sessions.values() if s.get('is_active', True))
        
        return {
            "total_sessions": len(sessions),
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "total_patients": len(patient_index),
            "storage_dir": str(self.storage_dir),
            "files": {
                "sessions": str(self.sessions_file),
                "messages": str(self.messages_file),
                "patient_index": str(self.patient_index_file)
            }
        }


# global storage instance
persistent_storage = PersistentChatStorage()