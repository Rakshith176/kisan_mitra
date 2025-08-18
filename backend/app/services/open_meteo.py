from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import httpx

from ..config import settings
from ..schemas import WeatherDailyItem


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_CURRENT_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoClient:
    """Client for Open-Meteo weather API"""
    
    def __init__(self):
        self.base_url = OPEN_METEO_BASE_URL
        self.current_url = OPEN_METEO_CURRENT_URL
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get current weather conditions for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Current weather data
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
            "timezone": "auto",
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(self.current_url, params=params)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
        
        current = data.get("current", {})
        
        # Map weather codes to descriptions
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        
        weather_code = current.get("weather_code", 0)
        weather_description = weather_codes.get(weather_code, "Unknown")
        
        return {
            "temperature_2m": current.get("temperature_2m"),
            "relative_humidity_2m": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed_10m": current.get("wind_speed_10m"),
            "weather_code_description": weather_description
        }
    
    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days to forecast (1-14)
            
        Returns:
            Weather forecast data
        """
        if days < 1 or days > 14:
            days = 7  # Default to 7 days
            
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_max,weather_code",
            "timezone": "auto",
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(self.base_url, params=params)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
        
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_t = daily.get("temperature_2m_max", [])
        min_t = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("wind_speed_10m_max", [])
        humidity = daily.get("relative_humidity_2m_max", [])
        weather_codes = daily.get("weather_code", [])
        
        # Map weather codes to descriptions
        weather_code_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        
        daily_forecasts = []
        for i in range(min(days, len(dates))):
            weather_code = weather_codes[i] if i < len(weather_codes) else 0
            daily_forecasts.append({
                "date": dates[i] if i < len(dates) else None,
                "temperature_2m_max": max_t[i] if i < len(max_t) else None,
                "temperature_2m_min": min_t[i] if i < len(min_t) else None,
                "precipitation_sum": precip[i] if i < len(precip) else None,
                "wind_speed_10m_max": wind[i] if i < len(wind) else None,
                "relative_humidity_2m_max": humidity[i] if i < len(humidity) else None,
                "weather_code_description": weather_code_map.get(weather_code, "Unknown")
            })
        
        return {
            "daily": daily_forecasts
        }


async def fetch_open_meteo_forecast(
    lat: float,
    lon: float,
    days: int = 7,
    api_key: Optional[str] = settings.open_meteo_api_key,
) -> List[WeatherDailyItem]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto",
    }
    headers: Dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(OPEN_METEO_BASE_URL, params=params, headers=headers)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    max_t = daily.get("temperature_2m_max", [])
    min_t = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    wind = daily.get("wind_speed_10m_max", [])

    items: List[WeatherDailyItem] = []
    for i, d in enumerate(dates[:days]):
        items.append(
            WeatherDailyItem(
                date=d,  # pydantic will parse str → datetime
                temp_min_c=float(min_t[i]) if i < len(min_t) else 0.0,
                temp_max_c=float(max_t[i]) if i < len(max_t) else 0.0,
                precipitation_mm=float(precip[i]) if i < len(precip) else None,
                wind_kph=float(wind[i]) if i < len(wind) else None,
            )
        )
    return items


