from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Tuple, Dict

import httpx


USER_AGENT = "farmer-backend/0.1 (+https://example.com)"
NOMINATIM_BASE = "https://nominatim.openstreetmap.org"


_FWD_CACHE: Dict[str, Tuple[float, float]] = {}
_REV_CACHE: Dict[Tuple[float, float], Tuple[Optional[str], Optional[str]]] = {}


async def geocode_market_name(name: str, district: Optional[str], state: Optional[str]) -> Optional[Tuple[float, float]]:
    parts = [name]
    if district:
        parts.append(district)
    if state:
        parts.append(state)
    parts.append("India")
    q = ", ".join(parts)
    if q in _FWD_CACHE:
        return _FWD_CACHE[q]
    params = {"q": q, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        resp = await client.get(f"{NOMINATIM_BASE}/search", params=params)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data:
            return None
        try:
            lat = float(data[0]["lat"])  # type: ignore[index]
            lon = float(data[0]["lon"])  # type: ignore[index]
            _FWD_CACHE[q] = (lat, lon)
            return lat, lon
        except Exception:
            return None


async def reverse_geocode(lat: float, lon: float) -> tuple[Optional[str], Optional[str]]:
    key = (round(lat, 3), round(lon, 3))
    if key in _REV_CACHE:
        return _REV_CACHE[key]
    params = {"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 10}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        resp = await client.get(f"{NOMINATIM_BASE}/reverse", params=params)
        if resp.status_code != 200:
            return None, None
        data = resp.json()
        address = data.get("address", {})
        # Nominatim varies by locale; try typical fields
        district = address.get("state_district") or address.get("county") or address.get("district")
        state = address.get("state")
        _REV_CACHE[key] = (district, state)
        return district, state


async def geocode_pincode(pincode: str) -> Optional[Tuple[float, float]]:
    # Cached lookup
    key = f"PIN:{pincode}"
    if key in _FWD_CACHE:
        return _FWD_CACHE[key]
    params = {"postalcode": pincode, "country": "India", "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        resp = await client.get(f"{NOMINATIM_BASE}/search", params=params)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data:
            # Fallback: free text search
            resp = await client.get(f"{NOMINATIM_BASE}/search", params={"q": f"{pincode}, India", "format": "json", "limit": 1})
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data:
                return None
        try:
            lat = float(data[0]["lat"])  # type: ignore[index]
            lon = float(data[0]["lon"])  # type: ignore[index]
            _FWD_CACHE[key] = (lat, lon)
            return (lat, lon)
        except Exception:
            return None


