from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, select

from .config import settings
from .logging_utils import configure_logging
import logging
from .db import engine, lifespan_db, get_db, AsyncSessionLocal
from .models import Crop, User, FarmerProfile, UserCropPreference, Conversation, ChatMessage, CropCycle, GrowthStage, CropTask, CropObservation, RiskAlert
from .schemas import (
    CropsResponse,
    CropItem,
    ProfileUpdateRequest,
    ProfileResponse,
    FeedResponse,
    GetChatMessagesResponse,
    ChatMessageDTO,
)
from .seeds import seed_crops
from .market_analysis.geocoding import geocode_pincode
from sqlalchemy.ext.asyncio import AsyncSession
from .feed.context import FeedContext
from .feed.builder import FeedBuilder
from .feed.generators import WeatherOverviewGenerator, DynamicCropTipsGenerator, MarketPricesGenerator, PriceTrendGenerator, KarnatakaMarketGenerator, KarnatakaLocationInsightsGenerator
from .chat.router import router as chat_router
from .chat.live_router import router as live_router
from .rag.router import router as rag_router
from .routers.crop_cycle import router as crop_cycle_router


def create_app() -> FastAPI:
    app = FastAPI(title="Farmer Assistant Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        configure_logging(settings.log_level)
        logging.getLogger(__name__).info("Starting backend; ensuring DB and seeds...")
        # Ensure local data dir exists for SQLite
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        # Create tables if not exist (Phase 0)
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        # Seed default crops if empty
        async with AsyncSessionLocal() as session:
            await seed_crops(session)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "env": settings.app_env}

    @app.post("/users", response_model=dict)
    async def create_user(
        client_id: str,
        language: str = "en",
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """Create a new user if it doesn't exist"""
        try:
            # Check if user already exists
            existing_user = await db.get(User, client_id)
            if existing_user:
                return {"message": "User already exists", "client_id": client_id}
            
            # Create new user
            new_user = User(
                client_id=client_id,
                language=language,
            )
            db.add(new_user)
            
            # Create basic farmer profile
            new_profile = FarmerProfile(
                id=client_id,
                client_id=client_id,
            )
            db.add(new_profile)
            
            await db.commit()
            
            return {
                "message": "User created successfully",
                "client_id": client_id,
                "language": language
            }
            
        except Exception as e:
            await db.rollback()
            logging.getLogger(__name__).error(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

    # Chat WebSocket endpoints (multimodal support)
    # Exposed at: /chat/ws/{session_id}
    app.include_router(chat_router)
    
    # Live API endpoints (real-time voice/text with tools)
    # Exposed at: /live/*
    app.include_router(live_router)
    
    # RAG endpoints
    # Exposed at: /rag/*
    app.include_router(rag_router)

    # Crop Cycle endpoints
    # Exposed at: /crop_cycle/*
    app.include_router(crop_cycle_router)

    # Chat history (for hydration)
    @app.get("/chat/messages", response_model=GetChatMessagesResponse)
    async def get_chat_messages(
        conversation_id: str,
        limit: int = 20,
        cursor: str | None = None,
        db: AsyncSession = Depends(get_db),
    ) -> GetChatMessagesResponse:
        # Decode cursor
        from base64 import b64decode
        from datetime import datetime as dt

        after_created_at: dt | None = None
        after_id: str | None = None
        if cursor:
            try:
                part = b64decode(cursor.encode()).decode()
                ts, after_id = part.split("|", 1)
                after_created_at = dt.fromisoformat(ts)
            except Exception:
                after_created_at, after_id = None, None

        from sqlalchemy import and_, or_, asc
        q = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
        if after_created_at and after_id:
            q = q.where(
                or_(
                    ChatMessage.created_at > after_created_at,
                    and_(ChatMessage.created_at == after_created_at, ChatMessage.id > after_id),
                )
            )
        q = q.order_by(asc(ChatMessage.created_at), asc(ChatMessage.id)).limit(limit + 1)
        result = await db.execute(q)
        rows = result.scalars().all()

        next_cursor = None
        has_more = False
        if len(rows) > limit:
            has_more = True
            rows = rows[:limit]
            last = rows[-1]
            from base64 import b64encode

            next_cursor = b64encode(f"{last.created_at.isoformat()}|{last.id}".encode()).decode()

        def to_dto(m: ChatMessage) -> ChatMessageDTO:
            return ChatMessageDTO(
                id=m.id,
                conversation_id=m.conversation_id,
                client_id=m.client_id,
                role=m.role,  # type: ignore[arg-type]
                type=m.type,  # type: ignore[arg-type]
                text=m.text,
                mime_type=m.mime_type,
                audio_path=m.audio_path,
                image_path=m.image_path,
                safety_blocked=m.safety_blocked,
                tokens_input=m.tokens_input,
                tokens_output=m.tokens_output,
                latency_ms=m.latency_ms,
                created_at=m.created_at,
            )

        return GetChatMessagesResponse(
            conversation_id=conversation_id,
            messages=[to_dto(m) for m in rows],
            cursor=next_cursor,
            has_more=has_more,
        )

    @app.get("/catalog/crops", response_model=CropsResponse)
    async def get_crops(db: AsyncSession = Depends(get_db)) -> CropsResponse:
        logging.getLogger(__name__).info("Fetching crops catalog")
        result = await db.execute(select(Crop))
        crops = result.scalars().all()
        return CropsResponse(
            crops=[
                CropItem(
                    id=c.id,
                    name_en=c.name_en,
                    name_hi=c.name_hi,
                    name_kn=c.name_kn,
                )
                for c in crops
            ]
        )

    @app.put("/profiles/{client_id}", response_model=ProfileResponse)
    async def upsert_profile(
        client_id: str,
        payload: ProfileUpdateRequest,
        db: AsyncSession = Depends(get_db),
    ) -> ProfileResponse:
        # Ensure user
        user = await db.get(User, client_id)
        if user is None:
            user = User(client_id=client_id, language=payload.language or "en")
            db.add(user)
        else:
            if payload.language:
                user.language = payload.language  # type: ignore[assignment]

        # Upsert profile
        profile = await db.get(FarmerProfile, client_id)
        if profile is None:
            profile = FarmerProfile(
                id=client_id,
                client_id=client_id,
                pincode=payload.pincode,
                lat=payload.lat,
                lon=payload.lon,
                farm_size=payload.farm_size,
                experience_years=payload.experience_years,
                irrigation_type=payload.irrigation_type,
                soil_type=payload.soil_type,
            )
            db.add(profile)
        else:
            if payload.pincode is not None:
                profile.pincode = payload.pincode
            if payload.lat is not None:
                profile.lat = payload.lat
            if payload.lon is not None:
                profile.lon = payload.lon
            if payload.farm_size is not None:
                profile.farm_size = payload.farm_size
            if payload.experience_years is not None:
                profile.experience_years = payload.experience_years
            if payload.irrigation_type is not None:
                profile.irrigation_type = payload.irrigation_type
            if payload.soil_type is not None:
                profile.soil_type = payload.soil_type

        # Update crop preferences
        if payload.crop_ids is not None:
            # Clear existing
            await db.execute(
                UserCropPreference.__table__.delete().where(
                    UserCropPreference.client_id == client_id
                )
            )
            for idx, crop_id in enumerate(payload.crop_ids):
                db.add(
                    UserCropPreference(
                        id=f"{client_id}:{crop_id}",
                        client_id=client_id,
                        crop_id=crop_id,
                        priority_score=float(len(payload.crop_ids) - idx),
                    )
                )

        await db.commit()

        # Response
        result = await db.execute(
            select(UserCropPreference.crop_id).where(
                UserCropPreference.client_id == client_id
            )
        )
        crop_ids = [row[0] for row in result.all()]
        return ProfileResponse(
            client_id=client_id,
            language=user.language,  # type: ignore[arg-type]
            pincode=profile.pincode,
            lat=profile.lat,
            lon=profile.lon,
            farm_size=profile.farm_size,
            experience_years=profile.experience_years,
            irrigation_type=profile.irrigation_type,
            soil_type=profile.soil_type,
            crop_ids=crop_ids,
        )

    @app.get("/feed", response_model=FeedResponse)
    async def get_feed(
        client_id: str,
        limit: int = 20,
        cursor: str | None = None,
        db: AsyncSession = Depends(get_db),
    ) -> FeedResponse:
        logging.getLogger(__name__).info("GET /feed for client_id=%s", client_id)
        user = await db.get(User, client_id)
        if user is None:
            raise HTTPException(status_code=404, detail="client_id not found")

        # Load profile for geo with pincode fallback
        profile = await db.get(FarmerProfile, client_id)
        lat = (profile.lat if profile else None)
        lon = (profile.lon if profile else None)
        if (lat is None or lon is None) and profile and profile.pincode:
            coords = await geocode_pincode(profile.pincode)
            if coords:
                lat, lon = coords
        lat = lat or 12.9716
        lon = lon or 77.5946

        # Build feed via independent generators
        builder = FeedBuilder(
            generators=[WeatherOverviewGenerator(), DynamicCropTipsGenerator(), MarketPricesGenerator(), PriceTrendGenerator(), KarnatakaMarketGenerator(), KarnatakaLocationInsightsGenerator()]
        )
        ctx = FeedContext(
            db=db,
            client_id=client_id,
            language=user.language,  # type: ignore[arg-type]
            lat=lat,
            lon=lon,
            pincode=profile.pincode if profile else None,
            crop_ids=None,
        )
        logging.getLogger(__name__).info("Building feed cards for client_id=%s", client_id)
        cards = await builder.build(ctx, limit=limit)

        return FeedResponse(
            client_id=client_id,
            language=user.language,  # type: ignore[arg-type]
            cards=cards,
            cursor=None,
            has_more=False,
        )

    return app


app = create_app()


