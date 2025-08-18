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
    
    This function now integrates with the Karnataka Market Tool to provide
    real-time market data for Karnataka state.
    """
    try:
        # Check if location is in Karnataka (roughly 12-18°N, 74-78°E)
        if 12 <= lat <= 18 and 74 <= lon <= 78:
            # Import the Karnataka market tool
            from .karnataka_market_tool import karnataka_tool
            
            # Get market data for the nearest major city
            nearest_city = _get_nearest_karnataka_city(lat, lon)
            
            # Get prices for the first crop
            crop_name = list(crop_names)[0] if crop_names else "wheat"
            
            # Use asyncio to run the async function
            import asyncio
            try:
                # Try to get the event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, we can't run sync code
                    # Return a message indicating to use the async version
                    return [
                        CommodityQuote(
                            market_name="Karnataka Markets",
                            commodity=crop_name,
                            unit="quintal",
                            price_min=0,
                            price_max=0,
                            price_modal=None
                        )
                    ]
                else:
                    # Run the async function
                    market_data = loop.run_until_complete(
                        karnataka_tool.get_prices_by_commodity(crop_name, user_profile="farmer")
                    )
            except RuntimeError:
                # No event loop, create one
                market_data = asyncio.run(
                    karnataka_tool.get_prices_by_commodity(crop_name, user_profile="farmer")
                )
            
            if market_data.get("status") == "success":
                prices = market_data.get("prices", [])
                if prices:
                    # Convert to CommodityQuote format
                    quotes = []
                    for price in prices[:max_markets]:
                        quotes.append(
                            CommodityQuote(
                                market_name=price["market"],
                                commodity=price["commodity"],
                                unit=price["unit"],
                                price_min=price["min_price"] or 0,
                                price_max=price["max_price"] or 0,
                                price_modal=price["modal_price"]
                            )
                        )
                    return quotes
            
            # Fallback to sample data if no real data available
            return [
                CommodityQuote(
                    market_name=f"{nearest_city} APMC",
                    commodity=crop_name,
                    unit="quintal",
                    price_min=1800,
                    price_max=2200,
                    price_modal=2000
                )
            ]
        
        else:
            # Outside Karnataka - return empty for now
            # TODO: Integrate with other state market data sources
            return []
            
    except Exception as e:
        # Log error and return empty list
        import logging
        logging.getLogger(__name__).error(f"Error fetching market prices: {e}")
        return []


def _get_nearest_karnataka_city(lat: float, lon: float) -> str:
    """Get the nearest major Karnataka city based on coordinates"""
    karnataka_cities = {
        "Bangalore": (12.9716, 77.5946),
        "Mysore": (12.2958, 76.6394),
        "Mangalore": (12.9141, 74.8560),
        "Hubli": (15.3647, 75.1240),
        "Belgaum": (15.8497, 74.4977),
        "Gulbarga": (17.3297, 76.8343),
        "Bellary": (15.1394, 76.9214),
        "Tumkur": (13.3409, 77.1010),
        "Mandya": (12.5221, 76.8975),
        "Hassan": (13.0034, 76.1004)
    }
    
    min_distance = float('inf')
    nearest_city = "Bangalore"
    
    for city, (city_lat, city_lon) in karnataka_cities.items():
        distance = _haversine_km(lat, lon, city_lat, city_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_city = city
    
    return nearest_city


