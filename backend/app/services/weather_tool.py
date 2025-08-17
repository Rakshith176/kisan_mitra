"""
Weather Tool for Agricultural Planning Agent
Provides weather data and crop-specific weather analysis
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.services.open_meteo import OpenMeteoClient

logger = logging.getLogger(__name__)

class WeatherTool:
    """Tool for providing weather information and crop-specific analysis"""
    
    def __init__(self):
        self.open_meteo = OpenMeteoClient()
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get current weather conditions for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Current weather data
        """
        try:
            weather_data = await self.open_meteo.get_current_weather(latitude, longitude)
            
            # Format for agent consumption
            return {
                "status": "success",
                "data": {
                    "temperature_celsius": weather_data.get("temperature_2m", "N/A"),
                    "humidity_percent": weather_data.get("relative_humidity_2m", "N/A"),
                    "precipitation_mm": weather_data.get("precipitation", "N/A"),
                    "wind_speed_kmh": weather_data.get("wind_speed_10m", "N/A"),
                    "weather_condition": weather_data.get("weather_code_description", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "location": {"lat": latitude, "lng": longitude}
                }
            }
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch weather data: {str(e)}"
            }
    
    async def get_weather_forecast(self, latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days to forecast (1-14)
            
        Returns:
            Weather forecast data
        """
        try:
            if days < 1 or days > 14:
                days = 7  # Default to 7 days
            
            forecast_data = await self.open_meteo.get_forecast(latitude, longitude, days)
            
            # Format daily forecasts
            daily_forecasts = []
            for i in range(min(days, len(forecast_data.get("daily", [])))):
                daily = forecast_data["daily"][i]
                daily_forecasts.append({
                    "date": daily.get("date", "N/A"),
                    "max_temp_celsius": daily.get("temperature_2m_max", "N/A"),
                    "min_temp_celsius": daily.get("temperature_2m_min", "N/A"),
                    "precipitation_mm": daily.get("precipitation_sum", "N/A"),
                    "humidity_percent": daily.get("relative_humidity_2m_max", "N/A"),
                    "wind_speed_kmh": daily.get("wind_speed_10m_max", "N/A"),
                    "weather_condition": daily.get("weather_code_description", "N/A")
                })
            
            return {
                "status": "success",
                "data": {
                    "forecast_days": days,
                    "daily_forecasts": daily_forecasts,
                    "location": {"lat": latitude, "lng": longitude},
                    "generated_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch forecast data: {str(e)}"
            }
    
    async def analyze_crop_weather_impact(self, latitude: float, longitude: float, crop_name: str) -> Dict[str, Any]:
        """
        Analyze weather impact on specific crops
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            crop_name: Name of the crop to analyze
            
        Returns:
            Crop-specific weather analysis
        """
        try:
            # Get current weather and forecast
            current = await self.get_current_weather(latitude, longitude)
            forecast = await self.get_weather_forecast(latitude, longitude, 7)
            
            if current["status"] == "error" or forecast["status"] == "error":
                return {
                    "status": "error",
                    "message": "Failed to fetch weather data for analysis"
                }
            
            # Basic crop weather analysis
            current_temp = current["data"]["temperature_celsius"]
            current_humidity = current["data"]["humidity_percent"]
            
            # Crop-specific weather thresholds (simplified)
            crop_thresholds = {
                "wheat": {"min_temp": 15, "max_temp": 30, "optimal_temp": 20, "humidity": "moderate"},
                "rice": {"min_temp": 20, "max_temp": 35, "optimal_temp": 25, "humidity": "high"},
                "maize": {"min_temp": 18, "max_temp": 32, "optimal_temp": 25, "humidity": "moderate"},
                "cotton": {"min_temp": 20, "max_temp": 35, "optimal_temp": 28, "humidity": "low"},
                "sugarcane": {"min_temp": 20, "max_temp": 38, "optimal_temp": 30, "humidity": "high"}
            }
            
            crop_info = crop_thresholds.get(crop_name.lower(), crop_thresholds["wheat"])
            
            # Analyze current conditions
            temp_status = "optimal"
            if current_temp < crop_info["min_temp"]:
                temp_status = "too_cold"
            elif current_temp > crop_info["max_temp"]:
                temp_status = "too_hot"
            
            # Generate recommendations
            recommendations = []
            if temp_status == "too_cold":
                recommendations.append("Consider delaying planting or use cold protection measures")
            elif temp_status == "too_hot":
                recommendations.append("Ensure adequate irrigation and consider shade protection")
            
            if current_humidity == "high" and crop_info["humidity"] == "low":
                recommendations.append("High humidity may increase disease risk - monitor for fungal issues")
            elif current_humidity == "low" and crop_info["humidity"] == "high":
                recommendations.append("Low humidity may require increased irrigation")
            
            return {
                "status": "success",
                "data": {
                    "crop_name": crop_name,
                    "current_weather": current["data"],
                    "weather_forecast": forecast["data"],
                    "analysis": {
                        "temperature_status": temp_status,
                        "optimal_temp_range": f"{crop_info['min_temp']}°C - {crop_info['max_temp']}°C",
                        "current_temp": f"{current_temp}°C",
                        "humidity_analysis": f"Current: {current_humidity}%, Optimal: {crop_info['humidity']}",
                        "recommendations": recommendations
                    },
                    "location": {"lat": latitude, "lng": longitude},
                    "analyzed_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing crop weather impact: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze weather impact: {str(e)}"
            }
    
    def get_tool_description(self) -> str:
        """Get tool description for the agent"""
        return """
        Weather Tool - Provides comprehensive weather information for agricultural planning.
        
        Available functions:
        1. get_current_weather(latitude, longitude) - Get current weather conditions
        2. get_weather_forecast(latitude, longitude, days) - Get weather forecast (1-14 days)
        3. analyze_crop_weather_impact(latitude, longitude, crop_name) - Analyze weather impact on specific crops
        
        Use this tool when you need:
        - Current weather conditions for a location
        - Weather forecasts for planning
        - Crop-specific weather analysis and recommendations
        - Weather risk assessment for farming decisions
        """
