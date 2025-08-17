from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    client_id: str = Field(primary_key=True, index=True)
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FarmerProfile(SQLModel, table=True):
    id: str = Field(primary_key=True)
    client_id: str = Field(foreign_key="user.client_id")
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    farm_size: Optional[float] = None
    experience_years: Optional[int] = None
    irrigation_type: Optional[str] = None
    soil_type: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Crop(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name_en: str
    name_hi: Optional[str] = None
    name_kn: Optional[str] = None
    aliases_json: Optional[str] = None


class UserCropPreference(SQLModel, table=True):
    id: str = Field(primary_key=True)
    client_id: str = Field(foreign_key="user.client_id")
    crop_id: str = Field(foreign_key="crop.id")
    priority_score: float = 1.0


class Conversation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    client_id: str = Field(foreign_key="user.client_id")
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(SQLModel, table=True):
    id: str = Field(primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    client_id: str = Field(foreign_key="user.client_id")
    role: str  # "user" | "assistant"
    type: str  # "text" | "audio" | "image"
    text: Optional[str] = None
    mime_type: Optional[str] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None
    safety_blocked: bool = False
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

