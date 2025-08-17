from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import LanguageCode


@dataclass
class FeedContext:
    db: AsyncSession
    client_id: str
    language: LanguageCode
    lat: float
    lon: float
    pincode: Optional[str] = None
    crop_ids: list[str] | None = None


