from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .nearest_markets import Mandi, pick_nearest_mandis
from .geocoding import geocode_market_name, reverse_geocode
from .agmarknet_client import fetch_prices
import logging


async def discover_mandis_near_user(*, lat: float, lon: float, commodity: str, k: int = 5) -> List[Mandi]:
    # Step 1: reverse geocode to get district/state
    logging.getLogger(__name__).info("Reverse geocoding lat=%s lon=%s", lat, lon)
    district, state = await reverse_geocode(lat, lon)

    # Step 2: query Agmarknet for recent records (last few days) in district/state for the commodity
    logging.getLogger(__name__).info("Fetching candidate markets for district=%s state=%s commodity=%s", district, state, commodity)
    rows = await fetch_prices(commodity=commodity, state=state, district=district, days=7, limit=500)

    # Step 3: extract unique market names
    markets: list[str] = []
    seen: set[str] = set()
    for r in rows:
        if r.market and r.market not in seen:
            seen.add(r.market)
            markets.append(r.market)

    # Step 4: geocode each market name lazily
    mandis: list[Mandi] = []
    for name in markets:
        coords = await geocode_market_name(name=name, district=district, state=state)
        if not coords:
            continue
        mlat, mlon = coords
        mandis.append(Mandi(name=name, lat=mlat, lon=mlon, district=district, state=state))

    # Step 5: pick nearest mandis to user
    nearest = pick_nearest_mandis(user_lat=lat, user_lon=lon, mandis=mandis, k=k)
    logging.getLogger(__name__).info("Nearest mandis selected: %d", len(nearest))
    return nearest


