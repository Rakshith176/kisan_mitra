"""
Market Tool for Agricultural Planning Agent
Provides market data and crop-specific market analysis
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.market_analysis.agmarknet_client import AgmarknetClient

logger = logging.getLogger(__name__)

class MarketTool:
    """Tool for providing market information and crop-specific market analysis"""
    
    def __init__(self):
        self.agmarknet = AgmarknetClient()
    
    async def get_current_prices(self, crop_name: str, state: str = None, district: str = None) -> Dict[str, Any]:
        """
        Get current market prices for a crop
        
        Args:
            crop_name: Name of the crop/commodity
            state: State name (optional)
            district: District name (optional)
            
        Returns:
            Current market price data
        """
        try:
            # Map crop names to commodity names for Agmarknet
            crop_to_commodity = {
                "wheat": "wheat",
                "rice": "rice",
                "maize": "maize",
                "cotton": "cotton",
                "sugarcane": "sugarcane",
                "pulses": "pulses",
                "oilseeds": "oilseeds"
            }
            
            commodity = crop_to_commodity.get(crop_name.lower(), crop_name.lower())
            
            # Get market prices
            prices = await self.agmarknet.get_market_prices(commodity, state, district)
            
            if not prices:
                return {
                    "status": "success",
                    "data": {
                        "crop_name": crop_name,
                        "commodity": commodity,
                        "prices": [],
                        "message": "No price data available for the specified criteria",
                        "location": {"state": state, "district": district},
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            # Format price data
            formatted_prices = []
            for price in prices[:10]:  # Limit to top 10 results
                formatted_prices.append({
                    "mandi_name": price.get("mandi_name", "N/A"),
                    "state": price.get("state", "N/A"),
                    "district": price.get("district", "N/A"),
                    "min_price": price.get("min_price", "N/A"),
                    "max_price": price.get("max_price", "N/A"),
                    "modal_price": price.get("modal_price", "N/A"),
                    "date": price.get("date", "N/A")
                })
            
            return {
                "status": "success",
                "data": {
                    "crop_name": crop_name,
                    "commodity": commodity,
                    "prices": formatted_prices,
                    "total_markets": len(prices),
                    "location": {"state": state, "district": district},
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error fetching market prices: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch market prices: {str(e)}"
            }
    
    async def get_price_trends(self, crop_name: str, state: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get price trends for a crop over time
        
        Args:
            crop_name: Name of the crop/commodity
            state: State name (optional)
            days: Number of days to analyze (7, 15, 30)
            
        Returns:
            Price trend analysis
        """
        try:
            if days not in [7, 15, 30]:
                days = 30  # Default to 30 days
            
            # Get historical prices (simplified - in real implementation, you'd fetch historical data)
            current_prices = await self.get_current_prices(crop_name, state)
            
            if current_prices["status"] == "error":
                return current_prices
            
            # Simulate trend analysis (in real implementation, you'd analyze historical data)
            prices = current_prices["data"]["prices"]
            if not prices:
                return {
                    "status": "success",
                    "data": {
                        "crop_name": crop_name,
                        "trend_period": f"{days} days",
                        "trend_analysis": "Insufficient data for trend analysis",
                        "recommendations": ["Collect more price data for trend analysis"],
                        "location": {"state": state},
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            # Basic trend analysis based on current prices
            modal_prices = [p["modal_price"] for p in prices if p["modal_price"] != "N/A"]
            if modal_prices:
                avg_price = sum(modal_prices) / len(modal_prices)
                price_range = max(modal_prices) - min(modal_prices)
                
                # Simple trend indicators
                if price_range < avg_price * 0.1:
                    trend = "stable"
                    trend_description = "Prices are relatively stable across markets"
                elif price_range < avg_price * 0.2:
                    trend = "moderate_variation"
                    trend_description = "Moderate price variation across markets"
                else:
                    trend = "high_variation"
                    trend_description = "High price variation across markets"
                
                recommendations = []
                if trend == "high_variation":
                    recommendations.append("Consider selling in markets with higher prices")
                    recommendations.append("Transport costs may be justified for better prices")
                elif trend == "stable":
                    recommendations.append("Prices are consistent - choose market based on convenience")
                
                return {
                    "status": "success",
                    "data": {
                        "crop_name": crop_name,
                        "trend_period": f"{days} days",
                        "current_analysis": {
                            "average_price": f"₹{avg_price:.2f}/quintal",
                            "price_range": f"₹{price_range:.2f}/quintal",
                            "trend": trend,
                            "trend_description": trend_description
                        },
                        "recommendations": recommendations,
                        "location": {"state": state},
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            return {
                "status": "success",
                "data": {
                    "crop_name": crop_name,
                    "trend_period": f"{days} days",
                    "trend_analysis": "Limited data available for trend analysis",
                    "recommendations": ["Monitor prices regularly for better trend analysis"],
                    "location": {"state": state},
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing price trends: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze price trends: {str(e)}"
            }
    
    async def get_market_recommendations(self, crop_name: str, state: str = None, district: str = None) -> Dict[str, Any]:
        """
        Get market recommendations for selling a crop
        
        Args:
            crop_name: Name of the crop/commodity
            state: State name (optional)
            district: District name (optional)
            
        Returns:
            Market recommendations
        """
        try:
            # Get current prices
            prices = await self.get_current_prices(crop_name, state, district)
            
            if prices["status"] == "error":
                return prices
            
            if not prices["data"]["prices"]:
                return {
                    "status": "success",
                    "data": {
                        "crop_name": crop_name,
                        "recommendations": ["No market data available for recommendations"],
                        "location": {"state": state, "district": district},
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            # Analyze prices and generate recommendations
            price_data = prices["data"]["prices"]
            
            # Find best markets
            valid_prices = [p for p in price_data if p["modal_price"] != "N/A"]
            if valid_prices:
                # Sort by modal price (highest first)
                sorted_prices = sorted(valid_prices, key=lambda x: x["modal_price"], reverse=True)
                
                best_markets = sorted_prices[:3]  # Top 3 markets
                worst_markets = sorted_prices[-3:]  # Bottom 3 markets
                
                recommendations = []
                recommendations.append(f"Best selling markets for {crop_name}:")
                for i, market in enumerate(best_markets, 1):
                    recommendations.append(f"{i}. {market['mandi_name']}, {market['district']} - ₹{market['modal_price']}/quintal")
                
                recommendations.append(f"\nMarkets to avoid:")
                for i, market in enumerate(worst_markets, 1):
                    recommendations.append(f"{i}. {market['mandi_name']}, {market['district']} - ₹{market['modal_price']}/quintal")
                
                # Additional insights
                avg_price = sum(p["modal_price"] for p in valid_prices) / len(valid_prices)
                price_variation = max(p["modal_price"] for p in valid_prices) - min(p["modal_price"] for p in valid_prices)
                
                if price_variation > avg_price * 0.3:
                    recommendations.append("\n💡 High price variation detected - consider transportation costs when choosing markets")
                elif price_variation < avg_price * 0.1:
                    recommendations.append("\n💡 Prices are consistent across markets - choose based on convenience")
                
                return {
                    "status": "success",
                    "data": {
                        "crop_name": crop_name,
                        "recommendations": recommendations,
                        "market_analysis": {
                            "total_markets": len(price_data),
                            "average_price": f"₹{avg_price:.2f}/quintal",
                            "price_variation": f"₹{price_variation:.2f}/quintal",
                            "best_price": f"₹{best_markets[0]['modal_price']}/quintal",
                            "worst_price": f"₹{worst_markets[0]['modal_price']}/quintal"
                        },
                        "location": {"state": state, "district": district},
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            return {
                "status": "success",
                "data": {
                    "crop_name": crop_name,
                    "recommendations": ["Insufficient price data for detailed recommendations"],
                    "location": {"state": state, "district": district},
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error generating market recommendations: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate market recommendations: {str(e)}"
            }
    
    def get_tool_description(self) -> str:
        """Get tool description for the agent"""
        return """
        Market Tool - Provides comprehensive market information for agricultural planning.
        
        Available functions:
        1. get_current_prices(crop_name, state, district) - Get current market prices
        2. get_price_trends(crop_name, state, days) - Get price trends over time
        3. get_market_recommendations(crop_name, state, district) - Get market recommendations for selling
        
        Use this tool when you need:
        - Current market prices for crops
        - Price trend analysis
        - Market recommendations for selling
        - Price comparison across markets
        - Market timing advice
        """
