"""
message conversion and serialization service
handles conversion between different message formats
"""

from typing import List, Any, Dict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """service for handling message conversions and serialization"""
    
    @staticmethod
    def convert_pydantic_to_langchain(messages: List[Any]) -> List[Any]:
        """convert pydantic messages to langchain message objects"""
        langchain_messages = []
        
        for msg in messages:
            try:
                if msg.role == "user":
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "ai":
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    langchain_messages.append(SystemMessage(content=msg.content))
            except Exception as e:
                logger.warning(f"failed to convert message: {e}")
                continue
        
        return langchain_messages
    
    @staticmethod
    def serialize_for_response(messages: List[Any]) -> List[Dict[str, Any]]:
        """serialize langchain messages for json response"""
        serialized = []
        
        for msg in messages:
            try:
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    # langchain message object
                    serialized.append({
                        "role": msg.type,
                        "content": str(msg.content)[:5000],  # limit content length
                        "name": getattr(msg, "name", None),
                    })
                elif isinstance(msg, dict):
                    # already a dict
                    serialized.append({
                        "role": msg.get("role", "unknown"),
                        "content": str(msg.get("content", ""))[:5000],
                        "name": msg.get("name", None)
                    })
                else:
                    # fallback
                    serialized.append({
                        "role": "unknown",
                        "content": str(msg)[:1000],
                        "name": None
                    })
            except Exception as e:
                logger.warning(f"failed to serialize message: {e}")
                serialized.append({
                    "role": "error",
                    "content": "message serialization failed",
                    "name": None
                })
        
        return serialized