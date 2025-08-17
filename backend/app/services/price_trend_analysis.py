from __future__ import annotations

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional, Any

from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini

from ..config import settings
from ..schemas import LocalizedText
from ..market_analysis.agmarknet_client import AgmarknetClient
from ..services.karnataka_market_tool import karnataka_tool


class PriceTrendAnalysisService:
    """Service for analyzing price trends using real market data"""
    
    def __init__(self):
        self.llm = Gemini(api_key=settings.google_api_key or "", model=settings.gemini_model)
        self.agmarknet_client = AgmarknetClient()
        self.logger = logging.getLogger(__name__)
    
    async def analyze_commodity_trends(
        self,
        commodity: str,
        lat: float,
        lon: float,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze price trends for a commodity using real market data
        
        Args:
            commodity: Name of the commodity/crop
            lat: User's latitude
            lon: User's longitude
            days: Number of days to analyze
            
        Returns:
            Comprehensive trend analysis with insights
        """
        try:
            # Determine user's location context
            location_context = self._get_location_context(lat, lon)
            
            # Collect price data from multiple sources
            price_data = await self._collect_price_data(commodity, location_context, days)
            
            if not price_data:
                return self._create_no_data_response(commodity, location_context)
            
            # Analyze trends
            trend_analysis = self._analyze_price_trends(price_data, days)
            
            # Generate insights using LLM
            insights = await self._generate_trend_insights(commodity, trend_analysis, location_context)
            
            return {
                "status": "success",
                "commodity": commodity,
                "location": location_context,
                "analysis_period": f"{days} days",
                "trend_analysis": trend_analysis,
                "insights": insights,
                "data_sources": self._get_data_sources(price_data),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trends for {commodity}: {e}")
            # Provide more context for debugging
            if "karnataka" in str(e).lower():
                self.logger.info(f"Karnataka data source issue detected for {commodity}")
            return self._create_error_response(commodity, str(e))
    
    async def _collect_price_data(
        self, 
        commodity: str, 
        location_context: Dict[str, Any], 
        days: int
    ) -> List[Dict[str, Any]]:
        """Collect price data from available sources"""
        price_data = []
        
        try:
            # 1. Try Agmarknet (national data)
            if location_context.get("state"):
                agmarknet_data = await self.agmarknet_client.get_price_trends(
                    commodity=commodity,
                    state=location_context["state"],
                    days=days
                )
                
                if agmarknet_data and agmarknet_data.get("status") == "success":
                    agmarknet_prices = agmarknet_data.get("data", {}).get("trend_data", [])
                    for price_point in agmarknet_prices:
                        price_data.append({
                            "source": "agmarknet",
                            "date": price_point.get("date"),
                            "price": price_point.get("price"),
                            "location": location_context["state"],
                            "commodity": commodity
                        })
            
            # 2. Try Karnataka data if user is in Karnataka
            if location_context.get("is_karnataka"):
                try:
                    karnataka_data = await karnataka_tool.get_prices_by_location(
                        location=location_context.get("nearest_district", "Bangalore")
                    )
                    
                    if karnataka_data and "commodities" in karnataka_data:
                        # Extract price data from Karnataka response
                        for commodity_name, market_prices in karnataka_data["commodities"].items():
                            if commodity_name.lower() in commodity.lower() or commodity.lower() in commodity_name.lower():
                                for market_price in market_prices:
                                    price_data.append({
                                        "source": "karnataka_government",
                                        "date": market_price.get("arrival_date", date.today().isoformat()),
                                        "price": market_price.get("modal_price", 0),
                                        "location": location_context.get("nearest_district"),
                                        "commodity": commodity_name,
                                        "market": market_price.get("market"),
                                        "min_price": market_price.get("min_price"),
                                        "max_price": market_price.get("max_price")
                                    })
                except Exception as e:
                    # Log but don't fail the entire analysis
                    self.logger.warning(f"Karnataka data collection failed for {commodity}: {e}")
                    # Continue with other data sources
            
            # 3. If no real data, return empty list (no mock data)
            if not price_data:
                self.logger.info(f"No price data available for {commodity} in {location_context.get('location_description', 'this region')}")
                return []
            
            # Sort by date and remove duplicates
            price_data = self._deduplicate_and_sort_prices(price_data)
            
            return price_data
            
        except Exception as e:
            self.logger.error(f"Error collecting price data: {e}")
            return []
    
    def _get_location_context(self, lat: float, lon: float) -> Dict[str, Any]:
        """Determine user's location context for data collection"""
        # Check if user is in Karnataka (roughly 11.5°N to 18.5°N and 74°E to 78.5°E)
        is_karnataka = 11.5 <= lat <= 18.5 and 74.0 <= lon <= 78.5
        
        # Major Karnataka districts with coordinates
        karnataka_districts = {
            "Bangalore": (12.9716, 77.5946),
            "Mysore": (12.2958, 76.6394),
            "Mangalore": (12.9141, 74.8560),
            "Belgaum": (15.8497, 74.4977),
            "Gulbarga": (17.3297, 76.8343),
            "Dharwad": (15.4589, 75.0078),
            "Bellary": (15.1394, 76.9214),
            "Bijapur": (16.8244, 75.7154),
            "Raichur": (16.2076, 77.3563),
            "Kolar": (13.1370, 78.1298),
            "Tumkur": (13.3409, 77.1011),
            "Mandya": (12.5221, 76.9009),
            "Hassan": (13.0033, 76.1004),
            "Shimoga": (13.9299, 75.5681),
            "Chitradurga": (14.2264, 76.4008)
        }
        
        # Find nearest district
        nearest_district = "Bangalore"
        min_distance = float('inf')
        
        for district, (loc_lat, loc_lon) in karnataka_districts.items():
            distance = ((lat - loc_lat) ** 2 + (lon - loc_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_district = district
        
        # Determine state based on coordinates
        if is_karnataka:
            state = "Karnataka"
        elif 28.0 <= lat <= 32.0 and 74.0 <= lon <= 78.0:
            state = "Punjab"
        elif 19.0 <= lat <= 22.0 and 72.0 <= lon <= 76.0:
            state = "Maharashtra"
        elif 25.0 <= lat <= 28.0 and 70.0 <= lon <= 78.0:
            state = "Rajasthan"
        else:
            state = "India"  # Default to national level
        
        return {
            "lat": lat,
            "lon": lon,
            "state": state,
            "is_karnataka": is_karnataka,
            "nearest_district": nearest_district if is_karnataka else None,
            "location_description": f"{nearest_district}, {state}" if is_karnataka else state
        }
    
    def _analyze_price_trends(self, price_data: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        """Analyze price trends using statistical methods"""
        if not price_data or len(price_data) < 2:
            return {
                "trend_direction": "insufficient_data",
                "price_change_percent": 0.0,
                "volatility_level": "unknown",
                "trend_strength": "unknown",
                "moving_averages": {},
                "price_range": {"min": 0, "max": 0, "avg": 0}
            }
        
        # Extract prices and dates
        prices = [p["price"] for p in price_data if p.get("price")]
        dates = [p["date"] for p in price_data if p.get("date")]
        
        if not prices:
            return {"trend_direction": "no_price_data", "price_change_percent": 0.0}
        
        # Calculate basic statistics
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Calculate price change
        first_price = prices[0]
        last_price = prices[-1]
        price_change = last_price - first_price
        price_change_percent = (price_change / first_price) * 100 if first_price > 0 else 0
        
        # Determine trend direction
        if price_change_percent > 5:
            trend_direction = "increasing"
        elif price_change_percent < -5:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Calculate volatility (standard deviation)
        variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        volatility_percent = (std_dev / avg_price) * 100 if avg_price > 0 else 0
        
        # Determine volatility level
        if volatility_percent < 5:
            volatility_level = "low"
        elif volatility_percent < 15:
            volatility_level = "medium"
        else:
            volatility_level = "high"
        
        # Calculate moving averages
        moving_averages = {}
        if len(prices) >= 7:
            moving_averages["7_day"] = sum(prices[-7:]) / 7
        if len(prices) >= 15:
            moving_averages["15_day"] = sum(prices[-15:]) / 15
        if len(prices) >= 30:
            moving_averages["30_day"] = sum(prices[-30:]) / 30
        
        # Calculate trend strength (linear regression slope)
        trend_strength = self._calculate_trend_strength(prices)
        
        return {
            "trend_direction": trend_direction,
            "price_change_percent": round(price_change_percent, 2),
            "volatility_level": volatility_level,
            "volatility_percent": round(volatility_percent, 2),
            "trend_strength": trend_strength,
            "moving_averages": {k: round(v, 2) for k, v in moving_averages.items()},
            "price_range": {
                "min": round(min_price, 2),
                "max": round(max_price, 2),
                "avg": round(avg_price, 2)
            },
            "data_points": len(prices),
            "price_data": price_data[-10:]  # Last 10 data points for context
        }
    
    def _calculate_trend_strength(self, prices: List[float]) -> str:
        """Calculate trend strength using linear regression"""
        if len(prices) < 2:
            return "unknown"
        
        n = len(prices)
        x_values = list(range(n))
        
        # Calculate linear regression
        sum_x = sum(x_values)
        sum_y = sum(prices)
        sum_xy = sum(x * y for x, y in zip(x_values, prices))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine strength based on slope
        if abs(slope) < 0.1:
            return "weak"
        elif abs(slope) < 0.5:
            return "moderate"
        else:
            return "strong"
    
    def _deduplicate_and_sort_prices(self, price_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate prices and sort by date"""
        # Create unique key for each price point
        seen = set()
        unique_prices = []
        
        for price_point in price_data:
            key = f"{price_point.get('date')}_{price_point.get('source')}_{price_point.get('location')}"
            if key not in seen:
                seen.add(key)
                unique_prices.append(price_point)
        
        # Sort by date (newest first)
        unique_prices.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return unique_prices
    
    async def _generate_trend_insights(
        self, 
        commodity: str, 
        trend_analysis: Dict[str, Any], 
        location_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights using Gemini LLM"""
        
        prompt = PromptTemplate(
            "You are an agricultural market analyst. Analyze the price trends for {commodity} and provide actionable insights.\n\n"
            "Context:\n"
            "- Commodity: {commodity}\n"
            "- Location: {location}\n"
            "- Analysis Period: {period}\n\n"
            "Trend Analysis:\n"
            "- Direction: {direction}\n"
            "- Price Change: {change_percent}%\n"
            "- Volatility: {volatility_level} ({volatility_percent}%)\n"
            "- Trend Strength: {trend_strength}\n"
            "- Price Range: ₹{min_price} - ₹{max_price} (Avg: ₹{avg_price})\n\n"
            "Provide insights in this JSON format:\n"
            "{{\n"
            '  "trend_summary": "2-3 sentence summary of the trend",\n'
            '  "selling_recommendations": ["3-4 actionable tips for farmers"],\n'
            '  "risk_assessment": "low|medium|high",\n'
            '  "next_week_outlook": "1-2 sentence prediction",\n'
            '  "market_opportunities": ["2-3 market opportunities"],\n'
            '  "confidence_score": 0.85\n'
            "}}\n\n"
            "Keep recommendations practical and farmer-friendly. Focus on immediate actions they can take."
        )
        
        try:
            # Format the prompt with actual data
            formatted_prompt = prompt.format(
                commodity=commodity,
                location=location_context.get("location_description", "India"),
                period=f"{trend_analysis.get('data_points', 0)} days",
                direction=trend_analysis.get("trend_direction", "unknown"),
                change_percent=trend_analysis.get("price_change_percent", 0),
                volatility_level=trend_analysis.get("volatility_level", "unknown"),
                volatility_percent=trend_analysis.get("volatility_percent", 0),
                trend_strength=trend_analysis.get("trend_strength", "unknown"),
                min_price=trend_analysis.get("price_range", {}).get("min", 0),
                max_price=trend_analysis.get("price_range", {}).get("max", 0),
                avg_price=trend_analysis.get("price_range", {}).get("avg", 0)
            )
            
            # Generate response using LLM
            response = await self.llm.acomplete(formatted_prompt)
            
            if response.text:
                try:
                    # Parse JSON response
                    insights = json.loads(response.text)
                    
                    # Validate required fields
                    required_fields = ["trend_summary", "selling_recommendations", "risk_assessment"]
                    if all(field in insights for field in required_fields):
                        return insights
                    
                except json.JSONDecodeError:
                    self.logger.debug("LLM response not in JSON format, using fallback insights")
            
            # Fallback insights if LLM fails
            return self._generate_fallback_insights(commodity, trend_analysis)
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return self._generate_fallback_insights(commodity, trend_analysis)
    
    def _generate_fallback_insights(self, commodity: str, trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback insights when LLM fails"""
        direction = trend_analysis.get("trend_direction", "stable")
        change_percent = trend_analysis.get("price_change_percent", 0)
        volatility = trend_analysis.get("volatility_level", "medium")
        
        # Generate basic insights based on trend data
        if direction == "increasing":
            summary = f"{commodity} prices are showing an upward trend with {change_percent}% increase."
            recommendations = [
                "Consider selling in the next 1-2 weeks to capture higher prices",
                "Monitor market conditions for optimal selling timing",
                "Check nearby markets for better price opportunities"
            ]
            risk = "low" if volatility == "low" else "medium"
            outlook = "Prices likely to remain strong in the short term."
            
        elif direction == "decreasing":
            summary = f"{commodity} prices are declining with {abs(change_percent)}% decrease."
            recommendations = [
                "Consider holding if possible until prices stabilize",
                "Explore alternative markets or storage options",
                "Monitor for price recovery signals"
            ]
            risk = "high"
            outlook = "Prices may continue to decline in the short term."
            
        else:
            summary = f"{commodity} prices are relatively stable with minimal change."
            recommendations = [
                "Monitor market conditions for price movements",
                "Consider selling when prices show upward momentum",
                "Maintain current storage and marketing plans"
            ]
            risk = "low"
            outlook = "Prices expected to remain stable in the short term."
        
        return {
            "trend_summary": summary,
            "selling_recommendations": recommendations,
            "risk_assessment": risk,
            "next_week_outlook": outlook,
            "market_opportunities": ["Monitor price trends", "Check multiple markets"],
            "confidence_score": 0.7
        }
    
    def _get_data_sources(self, price_data: List[Dict[str, Any]]) -> List[str]:
        """Get list of data sources used"""
        sources = set()
        for data_point in price_data:
            if data_point.get("source"):
                sources.add(data_point["source"])
        return list(sources)
    
    def _create_no_data_response(self, commodity: str, location_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create response when no price data is available"""
        return {
            "status": "no_data",
            "commodity": commodity,
            "location": location_context,
            "message": f"No price data available for {commodity} in {location_context.get('location_description', 'this region')}",
            "suggestions": [
                "Try a different commodity",
                "Check if data is available for nearby regions",
                "Contact local agricultural authorities for price information"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _create_error_response(self, commodity: str, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "commodity": commodity,
            "error": error_message,
            "message": "Failed to analyze price trends due to technical issues",
            "last_updated": datetime.utcnow().isoformat()
        }


# Global instance
price_trend_analysis_service = PriceTrendAnalysisService()
