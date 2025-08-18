from __future__ import annotations

from datetime import datetime, date
from typing import Literal, Optional, List

from pydantic import BaseModel, Field


LanguageCode = Literal["en", "hi", "kn"]


class LocalizedText(BaseModel):
    en: str
    hi: Optional[str] = None
    kn: Optional[str] = None


class WeatherDailyItem(BaseModel):
    date: datetime
    temp_min_c: float
    temp_max_c: float
    precipitation_mm: float | None = None
    wind_kph: float | None = None


class WeatherCard(BaseModel):
    card_type: Literal["weather"] = "weather"
    title: LocalizedText
    body_variants: list[LocalizedText] = Field(default_factory=list)
    location_name: Optional[str] = None
    lat: float
    lon: float
    forecast_days: list[WeatherDailyItem]
    # Action-first enhancements
    analysis: Optional[LocalizedText] = None
    recommendations: list[LocalizedText] = Field(default_factory=list)
    risk_tags: list[dict] = Field(default_factory=list)  # e.g., {type:"rain"|"heat"|"wind", severity:"low|med|high"}
    action_window_start: Optional[date] = None
    action_window_end: Optional[date] = None
    computed_at: Optional[datetime] = None
    data_window_days: Optional[int] = None


class MarketPriceItem(BaseModel):
    market_name: str
    commodity: str
    unit: str
    price_min: float
    price_max: float
    price_modal: float | None = None
    distance_km: float | None = None
    date: date = None


class MarketPricesCard(BaseModel):
    card_type: Literal["market_prices"] = "market_prices"
    title: LocalizedText
    body_variants: list[LocalizedText] = Field(default_factory=list)
    items: list[MarketPriceItem]
    analysis: LocalizedText | None = None
    recommendations: list[LocalizedText] = Field(default_factory=list)
    computed_at: datetime | None = None
    data_window_days: int | None = None
    freshness_date: date | None = None


class CropTipsCard(BaseModel):
    card_type: Literal["crop_tip"] = "crop_tip"
    title: LocalizedText
    body_variants: list[LocalizedText] = Field(default_factory=list)
    crop_id: str
    crop_name: LocalizedText


class PriceTrendCard(BaseModel):
    card_type: Literal["price_trend"] = "price_trend"
    title: LocalizedText
    body_variants: list[LocalizedText] = Field(default_factory=list)
    commodity: str
    trend_period: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    price_change_percent: float
    volatility_level: str  # "low", "medium", "high"
    selling_recommendations: list[LocalizedText]
    risk_assessment: str
    next_week_outlook: LocalizedText
    market_opportunities: list[LocalizedText]
    confidence_score: float
    data_source: str
    last_updated: datetime


class FeedCard(BaseModel):
    # Union-like: keep an explicit type field and shared fields
    card_id: str
    created_at: datetime
    language: LanguageCode
    data: WeatherCard | MarketPricesCard | CropTipsCard | PriceTrendCard | GeneralCard


class FeedResponse(BaseModel):
    client_id: str
    language: LanguageCode
    cards: list[FeedCard]
    cursor: Optional[str] = None
    has_more: bool = False


class CropItem(BaseModel):
    id: str
    name_en: str
    name_hi: Optional[str] = None
    name_kn: Optional[str] = None


class CropsResponse(BaseModel):
    crops: List[CropItem]


class ProfileUpdateRequest(BaseModel):
    language: Optional[LanguageCode] = None
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    farm_size: Optional[float] = None
    experience_years: Optional[int] = None
    irrigation_type: Optional[str] = None
    soil_type: Optional[str] = None
    crop_ids: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    client_id: str
    language: LanguageCode
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    farm_size: Optional[float] = None
    experience_years: Optional[int] = None
    irrigation_type: Optional[str] = None
    soil_type: Optional[str] = None
    crop_ids: List[str] = Field(default_factory=list)


class GeneralCard(BaseModel):
    card_type: Literal["general"] = "general"
    title: LocalizedText
    body_variants: list[LocalizedText] = Field(default_factory=list)
    severity: Optional[Literal["low", "med", "high"]] = None


# Chat schemas (Phase 2)
ChatRole = Literal["user", "assistant"]
ChatType = Literal["text", "audio", "image"]


class ChatMessageDTO(BaseModel):
    id: str
    conversation_id: str
    client_id: str
    role: ChatRole
    type: ChatType
    text: Optional[str] = None
    mime_type: Optional[str] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None
    safety_blocked: bool = False
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: int = 0
    created_at: datetime


class GetChatMessagesResponse(BaseModel):
    conversation_id: str
    messages: list[ChatMessageDTO]
    cursor: Optional[str] = None
    has_more: bool = False

