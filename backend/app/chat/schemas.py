"""
Chat schemas for multimodal conversations.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class MediaType(str, Enum):
    """Supported media types for chat."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


class ChatMessage(BaseModel):
    """Individual chat message."""
    id: str
    conversation_id: str
    client_id: str
    role: str = Field(..., description="user or assistant")
    media_type: MediaType
    content: str = Field(..., description="text content or base64 media data")
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Incoming chat request."""
    media_type: MediaType
    content: str = Field(..., description="text content or base64 media data")
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response from AI."""
    text: str
    audio: Optional[str] = Field(None, description="base64 encoded audio data")
    audio_mime_type: str = Field("audio/pcm;rate=16000;channels=1", description="audio format")
    metadata: Optional[Dict[str, Any]] = None


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str = Field(..., description="message type: request, response, error, ping")
    data: Optional[Union[ChatRequest, ChatResponse, Dict[str, Any]]] = None
    message_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationContext(BaseModel):
    """Conversation context for AI agent."""
    client_id: str
    conversation_id: str
    language: str = "en"
    crop_preferences: Optional[List[str]] = None
    location: Optional[Dict[str, float]] = None
    recent_messages: List[ChatMessage] = Field(default_factory=list)
    max_context_messages: int = 10
