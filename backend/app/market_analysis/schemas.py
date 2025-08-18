from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class MandiPriceRow(BaseModel):
    market: str
    state: Optional[str] = None
    district: Optional[str] = None
    commodity: str
    variety: Optional[str] = None
    unit: str
    modal: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    arrivals: Optional[float] = None
    date: date


class RankedMandiPrice(BaseModel):
    market: str
    distance_km: float
    modal: float
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    unit: str
    arrivals: Optional[float] = None
    date: date


