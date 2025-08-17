from __future__ import annotations

from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
from typing import Iterable, List, Optional


@dataclass
class Market:
    name: str
    lat: float
    lon: float


@dataclass
class CommodityQuote:
    market_name: str
    commodity: str
    unit: str
    price_min: float
    price_max: float
    price_modal: Optional[float] = None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = rlon2 - rlon1
    dlat = rlat2 - rlat1
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371.0 * c


# Simple static markets list (can be replaced by DB/API later)
_MARKETS: list[Market] = [
    Market(name="KR Market, Bengaluru", lat=12.9650, lon=77.5800),
    Market(name="Yeshwanthpur APMC", lat=13.0280, lon=77.5400),
    Market(name="Tumakuru APMC", lat=13.3409, lon=77.1010),
    Market(name="Mysuru APMC", lat=12.2958, lon=76.6394),
]


def get_nearby_market_prices(
    lat: float,
    lon: float,
    crop_names: Iterable[str],
    max_markets: int = 2,
) -> List[CommodityQuote]:
    """
    Get nearby market prices for crops.
    
    NOTE: This function currently returns empty results as it needs to be integrated
    with real market data sources like the Karnataka Market Tool or Agmarknet.
    
    TODO: Integrate with real market data sources to provide actual prices.
    """
    # TODO: Integrate with real market data sources
    # For now, return empty list to indicate no mock data is used
    
    return []


