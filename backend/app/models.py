from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List
from enum import Enum

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


# Crop Cycle Planning Models
class Season(str, Enum):
    """Agricultural seasons"""
    KHARIF = "kharif"
    RABI = "rabi"
    ZAID = "zaid"
    SUMMER = "summer"


class PlanStatus(str, Enum):
    """Status of crop planning"""
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressStatus(str, Enum):
    """Crop progress status"""
    NOT_STARTED = "not_started"
    PLANTED = "planted"
    GERMINATED = "germinated"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURING = "maturing"
    READY_FOR_HARVEST = "ready_for_harvest"
    HARVESTED = "harvested"


class TaskStatus(str, Enum):
    """Status of tracking tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class CropCycle(SQLModel, table=True):
    """Crop cycle planning and tracking"""
    __tablename__ = "crop_cycle"
    
    id: str = Field(primary_key=True)
    client_id: str = Field(foreign_key="user.client_id")
    crop_id: str = Field(foreign_key="crop.id")
    variety: str
    start_date: date
    season: Season
    pincode: str
    lat: float
    lon: float
    irrigation_type: str
    area_acres: float
    language: str
    status: PlanStatus
    planned_harvest_date: date
    actual_harvest_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GrowthStage(SQLModel, table=True):
    """Growth stage tracking for crop cycles"""
    __tablename__ = "growth_stage"
    
    id: str = Field(primary_key=True)
    cycle_id: str = Field(foreign_key="crop_cycle.id")
    stage_name: str  # "germination", "vegetative", "flowering", "maturity"
    expected_start_date: date
    actual_start_date: Optional[date] = None
    expected_duration_days: int
    progress_percentage: float
    notes: Optional[str] = None
    photos: Optional[str] = None  # JSON string of photo paths
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CropTask(SQLModel, table=True):
    """Tasks and checklists for crop cycles"""
    __tablename__ = "crop_task"
    
    id: str = Field(primary_key=True)
    cycle_id: str = Field(foreign_key="crop_cycle.id")
    task_name: str
    task_description: str
    task_type: str  # "observation", "action", "measurement"
    due_date: date
    completed_date: Optional[date] = None
    status: TaskStatus
    priority: str = "medium"  # "low", "medium", "high", "critical"
    notes: Optional[str] = None
    photos: Optional[str] = None  # JSON string of photo paths
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CropObservation(SQLModel, table=True):
    """Observations and measurements for crop cycles"""
    __tablename__ = "crop_observation"
    
    id: str = Field(primary_key=True)
    cycle_id: str = Field(foreign_key="crop_cycle.id")
    stage_name: str
    observation_date: date
    growth_percentage: float  # 0.0 to 100.0
    health_score: float  # 0.0 to 10.0
    observations: Optional[str] = None  # JSON string of observations
    photos: Optional[str] = None  # JSON string of photo paths
    weather_conditions: Optional[str] = None  # JSON string of weather data
    notes: str
    next_expected_milestone: str
    days_to_next_milestone: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RiskAlert(SQLModel, table=True):
    """Risk alerts and notifications for crop cycles"""
    __tablename__ = "risk_alert"
    
    id: str = Field(primary_key=True)
    cycle_id: str = Field(foreign_key="crop_cycle.id")
    alert_type: str  # "weather", "pest", "market", "soil"
    severity: str  # "info", "warning", "alert", "critical"
    title: str
    message: str
    risk_score: float  # 0.0 to 1.0
    mitigation_strategies: Optional[str] = None  # JSON string of strategies
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None

