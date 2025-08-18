"""Weather tool using Open-Meteo API for agricultural planning."""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Tuple
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WeatherInput(BaseModel):
    """Input schema for weather tool."""
    
    location: str = Field(default="", description="Location name, city, or coordinates (lat,lon). If not provided, will use user's profile location.")
    forecast_days: int = Field(default=7, description="Number of days for forecast (1-7)")
    include_agricultural_advice: bool = Field(default=True, description="Include agricultural recommendations based on weather")


class WeatherTool(BaseTool):
    """Tool for retrieving weather information for agricultural planning."""
    
    name: str = "get_weather_info"
    description: str = """
    Get comprehensive weather information for agricultural planning using Open-Meteo API.
    **IMPORTANT: This tool automatically uses the user's profile location - no need to specify location.**
    
    Use this tool when users ask about:
    - Current weather conditions for farming activities
    - Weather forecasts for crop planning
    - Agricultural recommendations based on weather
    - Temperature, humidity, and precipitation data
    - Wind conditions for spraying or harvesting
    
    The tool will automatically retrieve the user's location from their profile and provide
    weather information specific to their farming location.
    """
    
    args_schema: type[BaseModel] = WeatherInput
    
    def __init__(self):
        """Initialize the weather tool."""
        super().__init__()
        self._base_url = "https://api.open-meteo.com/v1"
        self._session = None
        
    async def _arun(self, **kwargs) -> str:
        """Run the weather tool asynchronously."""
        try:
            location = kwargs.get("location", "")
            forecast_days = min(max(kwargs.get("forecast_days", 7), 1), 7)
            include_advice = kwargs.get("include_agricultural_advice", True)
            context = kwargs.get("context", None)
            
            # If no location provided, try to get from context
            if not location and context and hasattr(context, 'location') and context.location:
                lat = context.location.get('lat')
                lon = context.location.get('lon')
                if lat and lon:
                    location = f"{lat},{lon}"
                    logger.info(f"Using location from user profile: {location}")
                else:
                    return "No location found in your profile. Please provide a location or update your profile with your coordinates."
            elif not location:
                return "Please provide a location for weather information, or ensure your location is set in your profile."
            
            # Parse location (could be coordinates or city name)
            lat, lon = await self._parse_location(location)
            if not lat or not lon:
                return f"Could not determine coordinates for location: {location}"
            
            # Get weather data
            weather_data = await self._fetch_weather_data(lat, lon, forecast_days)
            if not weather_data:
                return f"Unable to fetch weather data for {location}. Please try again later."
            
            # Format response
            response = self._format_weather_response(weather_data, location, include_advice)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in weather tool: {e}")
            return f"I encountered an error retrieving weather information: {str(e)}"
    
    def _run(self, **kwargs) -> str:
        """Run the weather tool (synchronous wrapper for async method)."""
        try:
            # Run the async method in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._arun(**kwargs))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running weather tool: {e}")
            return f"I encountered an error retrieving weather information: {str(e)}"
    
    async def _parse_location(self, location: str) -> Tuple[Optional[float], Optional[float]]:
        """Parse location string to get coordinates."""
        try:
            # Check if it's already coordinates
            if "," in location and location.count(",") == 1:
                parts = location.split(",")
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return lat, lon
            
            # For city names, we'd need a geocoding service
            # For now, return None to indicate we need coordinates
            # In a production system, you'd integrate with a geocoding API
            return None, None
            
        except (ValueError, IndexError):
            return None, None
    
    async def _fetch_weather_data(self, lat: float, lon: float, days: int) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo API."""
        try:
            # Create session if not exists
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            # Build API URL
            url = f"{self._base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
                "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
                "timezone": "auto",
                "forecast_days": days
            }
            
            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Weather API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def _format_weather_response(self, weather_data: Dict[str, Any], location: str, include_advice: bool) -> str:
        """Format weather data into a user-friendly response."""
        try:
            response = f"**Weather Information for {location}**\n\n"
            
            # Current weather
            if "current" in weather_data:
                current = weather_data["current"]
                response += "**Current Conditions:**\n"
                response += f"🌡️ Temperature: {current.get('temperature_2m', 'N/A')}°C\n"
                response += f"🌡️ Feels like: {current.get('apparent_temperature', 'N/A')}°C\n"
                response += f"💧 Humidity: {current.get('relative_humidity_2m', 'N/A')}%\n"
                response += f"🌧️ Precipitation: {current.get('precipitation', 'N/A')}mm\n"
                response += f"💨 Wind: {current.get('wind_speed_10m', 'N/A')} km/h\n"
                response += f"🧭 Wind Direction: {current.get('wind_direction_10m', 'N/A')}°\n"
                response += f"☁️ Weather: {self._get_weather_description(current.get('weather_code', 0))}\n\n"
            
            # Daily forecast
            if "daily" in weather_data:
                daily = weather_data["daily"]
                response += "**7-Day Forecast:**\n"
                
                for i in range(min(7, len(daily.get("time", [])))):
                    date = daily["time"][i]
                    max_temp = daily["temperature_2m_max"][i]
                    min_temp = daily["temperature_2m_min"][i]
                    precip = daily["precipitation_sum"][i]
                    precip_prob = daily["precipitation_probability_max"][i]
                    
                    # Format date
                    try:
                        date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%a, %b %d")
                    except:
                        formatted_date = date
                    
                    response += f"📅 {formatted_date}: {min_temp}°C - {max_temp}°C, "
                    response += f"🌧️ {precip}mm ({precip_prob}%)\n"
                
                response += "\n"
            
            # Agricultural advice
            if include_advice:
                response += "**Agricultural Recommendations:**\n"
                advice = self._generate_agricultural_advice(weather_data)
                response += advice
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting weather response: {e}")
            return "I retrieved weather data but encountered an error formatting it. Please try again."
    
    def _get_weather_description(self, code: int) -> str:
        """Convert weather code to description."""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")
    
    def _generate_agricultural_advice(self, weather_data: Dict[str, Any]) -> str:
        """Generate agricultural advice based on weather conditions."""
        try:
            advice = []
            
            # Get current conditions
            current = weather_data.get("current", {})
            current_temp = current.get("temperature_2m")
            current_humidity = current.get("relative_humidity_2m")
            current_precip = current.get("precipitation", 0)
            current_wind = current.get("wind_speed_10m")
            
            # Temperature-based advice
            if current_temp is not None:
                if current_temp < 10:
                    advice.append("❄️ Cold conditions - protect sensitive crops, avoid irrigation")
                elif current_temp > 35:
                    advice.append("🔥 Hot conditions - increase irrigation, provide shade for crops")
                elif 15 <= current_temp <= 30:
                    advice.append("🌱 Optimal temperature range for most crops")
            
            # Humidity-based advice
            if current_humidity is not None:
                if current_humidity > 80:
                    advice.append("💧 High humidity - monitor for fungal diseases, ensure good ventilation")
                elif current_humidity < 30:
                    advice.append("🌵 Low humidity - increase irrigation, consider misting systems")
            
            # Precipitation-based advice
            if current_precip > 5:
                advice.append("🌧️ Significant rainfall - avoid field work, check drainage systems")
            elif current_precip > 0:
                advice.append("🌦️ Light rainfall - good for crops, reduce irrigation if needed")
            
            # Wind-based advice
            if current_wind is not None:
                if current_wind > 20:
                    advice.append("💨 High winds - avoid spraying, protect young plants")
                elif current_wind > 10:
                    advice.append("🌬️ Moderate winds - suitable for most farming activities")
            
            # Daily forecast advice
            daily = weather_data.get("daily", {})
            if "precipitation_sum" in daily:
                total_precip = sum(daily["precipitation_sum"][:3])  # Next 3 days
                if total_precip > 20:
                    advice.append("📅 Heavy rainfall expected - plan field activities accordingly")
                elif total_precip > 5:
                    advice.append("📅 Moderate rainfall expected - good for crop growth")
            
            if not advice:
                advice.append("🌾 Weather conditions are favorable for most agricultural activities")
            
            return "\n".join(advice)
            
        except Exception as e:
            logger.error(f"Error generating agricultural advice: {e}")
            return "🌾 Weather conditions appear suitable for general farming activities"
    
    async def close_session(self):
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about the tool and its capabilities."""
        return {
            "tool_name": self.name,
            "description": self.description,
            "capabilities": [
                "Real-time weather data",
                "7-day weather forecast",
                "Agricultural recommendations",
                "Temperature and humidity monitoring",
                "Precipitation tracking",
                "Wind condition analysis"
            ],
            "data_source": "Open-Meteo API",
            "coverage": "Global weather data"
        }
