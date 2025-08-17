from __future__ import annotations

from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
from typing import Iterable, List


@dataclass
class Mandi:
    name: str
    lat: float
    lon: float
    district: str | None = None
    state: str | None = None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = rlon2 - rlon1
    dlat = rlat2 - rlat1
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371.0 * c


def pick_nearest_mandis(
    *, user_lat: float, user_lon: float, mandis: Iterable[Mandi], k: int = 5
) -> List[Mandi]:
    return sorted(mandis, key=lambda m: _haversine_km(user_lat, user_lon, m.lat, m.lon))[:k]


