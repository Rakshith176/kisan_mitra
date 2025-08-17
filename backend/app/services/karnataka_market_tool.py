from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
import json

from ..market_analysis.karnataka_client import fetch_karnataka_prices
from ..market_analysis.schemas import MandiPriceRow


class KarnatakaMarketTool:
    """Tool for fetching market prices from Karnataka government website with AI insights"""
    
    def __init__(self):
        self.name = "karnataka_market_prices"
        self.description = "Fetch agricultural market prices from Karnataka government website with AI insights"
        self.logger = logging.getLogger(__name__)
        self.max_retries = 2
        self.retry_delay = 1.0  # seconds
        
        # User profile preferences for filtering
        self.user_preferences = {
            "farmer": {
                "crops": ["wheat", "rice", "jowar", "bajra", "onion", "potato", "tomato"],
                "priority": "price_trends",
                "insights_focus": ["best_selling_time", "price_predictions", "market_demand"]
            },
            "trader": {
                "crops": ["all"],
                "priority": "market_volatility",
                "insights_focus": ["arbitrage_opportunities", "supply_demand", "export_potential"]
            },
            "consumer": {
                "crops": ["vegetables", "fruits", "pulses"],
                "priority": "price_affordability",
                "insights_focus": ["best_buying_time", "seasonal_trends", "quality_indicators"]
            }
        }
        
    async def get_prices_by_location(
        self, 
        location: str, 
        date_str: Optional[str] = None,
        report_type: str = "M",
        user_profile: str = "farmer"
    ) -> Dict[str, Any]:
        """
        Get market prices for a specific location in Karnataka with AI insights
        
        Args:
            location: District or market name (e.g., "Bangalore", "Mysore", "Mangalore")
            date_str: Date in DD/MM/YYYY format (defaults to today)
            report_type: Type of report - M=MarketWise, C=Commoditywise, L=Latest
            user_profile: User profile for filtering and insights (farmer, trader, consumer)
            
        Returns:
            Dictionary containing price data, AI insights, and metadata
        """
        try:
            # Input validation
            if not location or not location.strip():
                return {
                    "error": "Location cannot be empty or contain only whitespace",
                    "location": location,
                    "status": "error",
                    "data_source": "karnataka_government"
                }
            
            # Clean and validate location
            location = location.strip()
            if len(location) > 100:  # Reasonable limit for location names
                return {
                    "error": "Location name is too long (maximum 100 characters)",
                    "location": location,
                    "status": "error",
                    "data_source": "karnataka_government"
                }
            
            # Validate report_type
            valid_report_types = ["M", "C", "L", "S"]
            if report_type not in valid_report_types:
                return {
                    "error": f"Invalid report_type. Must be one of: {', '.join(valid_report_types)}",
                    "report_type": report_type,
                    "valid_types": valid_report_types,
                    "status": "error",
                    "data_source": "karnataka_government"
                }
            
            # Validate user_profile
            valid_profiles = ["farmer", "trader", "consumer"]
            if user_profile not in valid_profiles:
                user_profile = "farmer"  # Default to farmer
                
            # Parse date if provided
            report_date = None
            if date_str:
                try:
                    day, month, year = date_str.split('/')
                    day, month, year = int(day), int(month), int(year)
                    
                    # Validate date components
                    if year < 1900 or year > 2100:
                        return {
                            "error": "Year must be between 1900 and 2100",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                    
                    if month < 1 or month > 12:
                        return {
                            "error": "Month must be between 1 and 12",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                    
                    if day < 1 or day > 31:
                        return {
                            "error": "Day must be between 1 and 31",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                    
                    report_date = date(year, month, day)
                    
                    # Check if date is in the future
                    if report_date > date.today():
                        return {
                            "error": "Date cannot be in the future",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                        
                except ValueError as e:
                    return {
                        "error": f"Invalid date format: {str(e)}. Please use DD/MM/YYYY format.",
                        "date": date_str,
                        "example": "15/08/2024",
                        "status": "error",
                        "data_source": "karnataka_government"
                    }
            
            # Use the working main page approach instead of the broken reports system
            print("🏠 Using main page data source (reports system is currently down)")
            
            # Get data from the main page which actually contains market information
            price_list = await fetch_karnataka_prices(location=location)
            
            if not price_list:
                self.logger.warning(f"No price data found for {location} from main page")
                return {
                    "error": "No market data available at the moment",
                    "location": location,
                    "date": date_str or "today",
                    "data_source": "karnataka_government_main_page",
                    "status": "no_data",
                    "suggestions": [
                        "The Karnataka government website may be experiencing issues",
                        "Try again later when the website is fully functional",
                        "Check the government website directly for current prices"
                    ]
                }
            
            # Filter data based on user profile
            filtered_prices = self._filter_by_user_profile(price_list, user_profile)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(filtered_prices, user_profile)
            
            # Convert to the expected format
            markets = {}
            for price in filtered_prices:
                market_name = price.market
                if market_name not in markets:
                    markets[market_name] = []
                
                markets[market_name].append({
                    "commodity": price.commodity,
                    "variety": price.variety,
                    "unit": price.unit,
                    "modal_price": price.modal,
                    "min_price": price.min_price,
                    "max_price": price.max_price,
                    "arrival_date": price.date.isoformat(),
                    "arrivals": price.arrivals
                })
            
            self.logger.info(f"Successfully fetched {len(filtered_prices)} price records for {location} from main page with {user_profile} profile")
            
            return {
                "markets": markets,
                "location": location,
                "date": date_str or "today",
                "data_source": "karnataka_government_main_page",
                "status": "success",
                "total_records": len(filtered_prices),
                "user_profile": user_profile,
                "ai_insights": ai_insights,
                "price_list": filtered_prices,  # Include the actual price list for feed service
                "note": "Data extracted from main page due to reports system issues"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch prices for {location}: {e}")
            
            # Check if it's a server error
            if "500" in str(e) or "Internal Server Error" in str(e):
                self.logger.warning(f"Karnataka website server error for {location}, providing fallback data")
                return self._get_fallback_market_info(location)
            
            return {
                "error": f"Failed to fetch prices: {str(e)}",
                "location": location,
                "date": date_str or "today",
                "data_source": "karnataka_government",
                "status": "error",
                "suggestions": [
                    "Check your internet connection",
                    "Try again in a few minutes",
                    "The government website may be temporarily unavailable"
                ]
            }
    
    async def _fetch_with_retry(
        self, 
        location: str, 
        report_date: Optional[date], 
        report_type: str
    ) -> List[MandiPriceRow]:
        """Fetch prices with retry mechanism for temporary failures"""
        
        # Use local delay to avoid modifying global instance
        local_delay = self.retry_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                prices = await fetch_karnataka_prices(
                    location=location,
                    report_date=report_date,
                    report_type=report_type
                )
                
                if prices:
                    self.logger.info(f"Successfully fetched {len(prices)} price records for {location}")
                    return prices
                else:
                    self.logger.info(f"No price data found for {location} (attempt {attempt + 1})")
                    
            except Exception as e:
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {location}: {e}")
                    self.logger.info(f"Retrying in {local_delay} seconds...")
                    await asyncio.sleep(local_delay)
                    # Increase delay for next retry (local only)
                    local_delay *= 1.5
                else:
                    self.logger.error(f"All {self.max_retries + 1} attempts failed for {location}: {e}")
                    raise
        
        return []
    
    async def get_commodity_prices(
        self, 
        commodity: str, 
        date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get prices for a specific commodity across Karnataka markets
        
        Args:
            commodity: Name of the commodity
            date_str: Date in DD/MM/YYYY format (defaults to today)
            
        Returns:
            Dictionary containing price data and metadata
        """
        try:
            # Input validation
            if not commodity or not commodity.strip():
                return {
                    "error": "Commodity cannot be empty or contain only whitespace",
                    "commodity": commodity,
                    "status": "error",
                    "data_source": "karnataka_government"
                }
            
            # Clean and validate commodity
            commodity = commodity.strip()
            if len(commodity) > 100:  # Reasonable limit for commodity names
                return {
                    "error": "Commodity name is too long (maximum 100 characters)",
                    "commodity": commodity,
                    "status": "error",
                    "data_source": "karnataka_government"
                }

            # Parse date if provided
            report_date = None
            if date_str:
                try:
                    day, month, year = date_str.split('/')
                    day, month, year = int(day), int(month), int(year)
                    
                    # Validate date components
                    if year < 1900 or year > 2100:
                        return {
                            "error": "Year must be between 1900 and 2100",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                    
                    if month < 1 or month > 12:
                        return {
                            "error": "Month must be between 1 and 12",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                    
                    if day < 1 or day > 31:
                        return {
                            "error": "Day must be between 1 and 31",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                    
                    report_date = date(year, month, day)
                    
                    # Check if date is in the future
                    if report_date > date.today():
                        return {
                            "error": "Date cannot be in the future",
                            "date": date_str,
                            "example": "15/08/2024",
                            "status": "error",
                            "data_source": "karnataka_government"
                        }
                        
                except ValueError as e:
                    return {
                        "error": f"Invalid date format: {str(e)}. Please use DD/MM/YYYY format.",
                        "date": date_str,
                        "example": "15/08/2024",
                        "status": "error",
                        "data_source": "karnataka_government"
                    }
            
            # Try to fetch commodity prices with retry mechanism
            prices = await self._fetch_commodity_with_retry(commodity, report_date)
            
            if not prices:
                return {
                    "message": f"No price data found for {commodity}",
                    "commodity": commodity,
                    "date": report_date.isoformat() if report_date else "today",
                    "suggestions": [
                        "Try a different date",
                        "Check if the commodity name is correct",
                        "The government website may be temporarily unavailable"
                    ],
                    "data_source": "karnataka_government",
                    "status": "no_data"
                }
            
            # Group by market for better organization
            market_groups = {}
            for price in prices:
                if price.market not in market_groups:
                    market_groups[price.market] = []
                market_groups[price.market].append({
                    "commodity": price.commodity,
                    "variety": price.variety,
                    "min_price": price.min_price,
                    "max_price": price.max_price,
                    "modal_price": price.modal,
                    "arrival_date": price.arrivals
                })
            
            # Log successful operation
            self.logger.info(f"Successfully processed {len(prices)} price records for commodity {commodity}")
            
            return {
                "commodity": commodity,
                "date": report_date.isoformat() if report_date else "today",
                "total_markets": len(market_groups),
                "markets": market_groups,
                "summary": {
                    "avg_min_price": sum(p.min_price for p in prices) / len(prices) if prices else 0,
                    "avg_max_price": sum(p.max_price for p in prices) / len(prices) if prices else 0,
                    "avg_modal_price": sum(p.modal for p in prices) / len(prices) if prices else 0
                },
                "data_source": "karnataka_government",
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch commodity prices for {commodity}: {e}")
            
            # Check if it's a server error
            if "500" in str(e) or "Internal Server Error" in str(e):
                self.logger.warning(f"Karnataka website server error for commodity {commodity}, providing fallback data")
                fallback_data = self._get_fallback_market_info("Karnataka")
                fallback_data["commodity"] = commodity
                return fallback_data
            
            return {
                "error": f"Failed to fetch commodity prices: {str(e)}",
                "commodity": commodity,
                "date": date_str or "today",
                "data_source": "karnataka_government",
                "status": "error",
                "suggestions": [
                    "Check your internet connection",
                    "Try again in a few minutes",
                    "The government website may be temporarily unavailable"
                ]
            }
    
    async def _fetch_commodity_with_retry(
        self, 
        commodity: str, 
        report_date: Optional[date]
    ) -> List[MandiPriceRow]:
        """Fetch commodity prices with retry mechanism for temporary failures"""
        
        # Use local delay to avoid modifying global instance
        local_delay = self.retry_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                prices = await fetch_karnataka_prices(
                    commodity=commodity,
                    report_date=report_date
                )
                
                if prices:
                    self.logger.info(f"Successfully fetched {len(prices)} price records for {commodity}")
                    return prices
                else:
                    self.logger.info(f"No price data found for {commodity} (attempt {attempt + 1})")
                    
            except Exception as e:
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {commodity}: {e}")
                    self.logger.info(f"Retrying in {local_delay} seconds...")
                    await asyncio.sleep(local_delay)
                    # Increase delay for next retry (local only)
                    local_delay *= 1.5
                else:
                    self.logger.error(f"All {self.max_retries + 1} attempts failed for {commodity}: {e}")
                    raise
        
        return []

    def _filter_by_user_profile(self, price_list: List[MandiPriceRow], user_profile: str = "farmer") -> List[MandiPriceRow]:
        """Filter market data based on user profile preferences"""
        if not price_list:
            return []
            
        preferences = self.user_preferences.get(user_profile, self.user_preferences["farmer"])
        preferred_crops = preferences["crops"]
        
        if "all" in preferred_crops:
            return price_list
            
        # Filter by preferred crops
        filtered_prices = []
        for price in price_list:
            commodity_lower = price.commodity.lower()
            
            # Check if this commodity matches any preferred crop
            if any(crop in commodity_lower for crop in preferred_crops):
                filtered_prices.append(price)
            # Also check for category matches (vegetables, fruits, pulses)
            elif any(category in commodity_lower for category in ["vegetable", "fruit", "pulse"]):
                if any(category in preferred_crops for category in ["vegetables", "fruits", "pulses"]):
                    filtered_prices.append(price)
                    
        self.logger.info(f"Filtered {len(price_list)} prices to {len(filtered_prices)} for {user_profile} profile")
        return filtered_prices

    def _generate_ai_insights(self, price_list: List[MandiPriceRow], user_profile: str = "farmer") -> Dict[str, Any]:
        """Generate AI-powered insights from market data"""
        if not price_list:
            return {"insights": [], "summary": "No data available for insights"}
            
        preferences = self.user_preferences.get(user_profile, self.user_preferences["farmer"])
        insights_focus = preferences["insights_focus"]
        
        insights = []
        
        # Analyze price trends
        if "price_trends" in preferences["priority"] or "price_predictions" in insights_focus:
            price_analysis = self._analyze_price_trends(price_list)
            insights.append(price_analysis)
            
        # Market demand analysis
        if "market_demand" in insights_focus:
            demand_analysis = self._analyze_market_demand(price_list)
            insights.append(demand_analysis)
            
        # Best timing insights
        if "best_selling_time" in insights_focus or "best_buying_time" in insights_focus:
            timing_insights = self._analyze_best_timing(price_list, user_profile)
            insights.append(timing_insights)
            
        # Seasonal trends
        if "seasonal_trends" in insights_focus:
            seasonal_analysis = self._analyze_seasonal_trends(price_list)
            insights.append(seasonal_analysis)
            
        # Arbitrage opportunities for traders
        if "arbitrage_opportunities" in insights_focus:
            arbitrage_analysis = self._analyze_arbitrage_opportunities(price_list)
            insights.append(arbitrage_analysis)
            
        return {
            "insights": insights,
            "summary": f"Generated {len(insights)} AI insights for {user_profile} profile",
            "focus_areas": insights_focus
        }

    def _analyze_price_trends(self, price_list: List[MandiPriceRow]) -> Dict[str, Any]:
        """Analyze price trends and patterns"""
        if not price_list:
            return {"type": "price_trends", "message": "No data for price analysis"}
            
        # Calculate price statistics
        prices = [price.modal for price in price_list if price.modal > 0]
        if not prices:
            return {"type": "price_trends", "message": "No valid prices for analysis"}
            
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        price_range = max_price - min_price
        
        # Identify high-value crops
        high_value_crops = [price for price in price_list if price.modal > avg_price * 1.5]
        low_value_crops = [price for price in price_list if price.modal < avg_price * 0.5]
        
        return {
            "type": "price_trends",
            "summary": f"Market shows {len(price_list)} commodities with average price ₹{avg_price:.0f}/quintal",
            "statistics": {
                "average_price": round(avg_price, 2),
                "price_range": round(price_range, 2),
                "highest_price": max_price,
                "lowest_price": min_price
            },
            "high_value_crops": [f"{crop.commodity} (₹{crop.modal}/quintal)" for crop in high_value_crops[:5]],
            "low_value_crops": [f"{crop.commodity} (₹{crop.modal}/quintal)" for crop in low_value_crops[:5]],
            "recommendation": "Focus on high-value crops for better returns"
        }
        
    def _analyze_market_demand(self, price_list: List[MandiPriceRow]) -> Dict[str, Any]:
        """Analyze market demand patterns"""
        if not price_list:
            return {"type": "market_demand", "message": "No data for demand analysis"}
            
        # Group by commodity category
        categories = {}
        for price in price_list:
            category = self._get_commodity_category(price.commodity)
            if category not in categories:
                categories[category] = []
            categories[category].append(price)
            
        # Analyze demand by category
        category_analysis = {}
        for category, prices in categories.items():
            avg_price = sum(p.modal for p in prices) / len(prices)
            category_analysis[category] = {
                "count": len(prices),
                "avg_price": round(avg_price, 2),
                "price_range": f"₹{min(p.modal for p in prices)} - ₹{max(p.modal for p in prices)}"
            }
            
        return {
            "type": "market_demand",
            "summary": f"Market covers {len(categories)} major categories",
            "category_breakdown": category_analysis,
            "recommendation": "Diversify across categories to spread risk"
        }
        
    def _analyze_best_timing(self, price_list: List[MandiPriceRow], user_profile: str) -> Dict[str, Any]:
        """Analyze best timing for buying/selling"""
        if not price_list:
            return {"type": "timing_analysis", "message": "No data for timing analysis"}
            
        # Simple timing logic based on current month
        current_month = date.today().month
        
        if user_profile == "farmer":
            if current_month in [10, 11, 12]:  # Oct-Dec
                timing = "Harvest season - good time to sell grains"
            elif current_month in [6, 7, 8]:   # Jun-Aug
                timing = "Monsoon season - prices may be higher due to supply constraints"
            else:
                timing = "Moderate season - monitor prices for best selling opportunity"
        else:  # consumer
            if current_month in [6, 7, 8]:   # Jun-Aug
                timing = "Monsoon season - prices may be higher, consider buying before"
            elif current_month in [10, 11, 12]:  # Oct-Dec
                timing = "Harvest season - prices likely lower, good time to buy"
            else:
                timing = "Moderate season - prices stable, good time to buy"
                
        return {
            "type": "timing_analysis",
            "current_month": current_month,
            "timing_recommendation": timing,
            "action": "sell" if user_profile == "farmer" else "buy"
        }
        
    def _analyze_seasonal_trends(self, price_list: List[MandiPriceRow]) -> Dict[str, Any]:
        """Analyze seasonal price patterns"""
        if not price_list:
            return {"type": "seasonal_trends", "message": "No data for seasonal analysis"}
            
        # Group by commodity for seasonal analysis
        commodity_prices = {}
        for price in price_list:
            if price.commodity not in commodity_prices:
                commodity_prices[price.commodity] = []
            commodity_prices[price.commodity].append(price.modal)
            
        seasonal_insights = []
        for commodity, prices in commodity_prices.items():
            if len(prices) > 1:
                price_variance = max(prices) - min(prices)
                if price_variance > sum(prices) / len(prices) * 0.3:  # 30% variance
                    seasonal_insights.append(f"{commodity} shows seasonal price variation")
                    
        return {
            "type": "seasonal_trends",
            "summary": f"Found {len(seasonal_insights)} commodities with seasonal patterns",
            "insights": seasonal_insights,
            "recommendation": "Plan activities around seasonal price patterns"
        }
        
    def _analyze_arbitrage_opportunities(self, price_list: List[MandiPriceRow]) -> Dict[str, Any]:
        """Analyze arbitrage opportunities for traders"""
        if not price_list:
            return {"type": "arbitrage_analysis", "message": "No data for arbitrage analysis"}
            
        # Find price differences between varieties of same commodity
        commodity_varieties = {}
        for price in price_list:
            if price.commodity not in commodity_varieties:
                commodity_varieties[price.commodity] = []
            commodity_varieties[price.commodity].append(price)
            
        arbitrage_opportunities = []
        for commodity, varieties in commodity_varieties.items():
            if len(varieties) > 1:
                prices = [v.modal for v in varieties]
                max_price = max(prices)
                min_price = min(prices)
                price_diff = max_price - min_price
                
                if price_diff > min_price * 0.2:  # 20% difference
                    arbitrage_opportunities.append({
                        "commodity": commodity,
                        "price_difference": round(price_diff, 2),
                        "varieties": len(varieties),
                        "opportunity": f"Buy {commodity} varieties at ₹{min_price} and sell at ₹{max_price}"
                    })
                    
        return {
            "type": "arbitrage_analysis",
            "summary": f"Found {len(arbitrage_opportunities)} arbitrage opportunities",
            "opportunities": arbitrage_opportunities[:5],  # Top 5
            "recommendation": "Focus on high price-difference commodities for arbitrage"
        }
        
    def _get_commodity_category(self, commodity: str) -> str:
        """Get commodity category for analysis"""
        commodity_lower = commodity.lower()
        
        if any(crop in commodity_lower for crop in ["wheat", "rice", "jowar", "bajra", "maize"]):
            return "Cereals"
        elif any(crop in commodity_lower for crop in ["onion", "potato", "tomato", "cauliflower"]):
            return "Vegetables"
        elif any(crop in commodity_lower for crop in ["apple", "banana", "mango", "orange"]):
            return "Fruits"
        elif any(crop in commodity_lower for crop in ["pulse", "dal", "gram"]):
            return "Pulses"
        elif any(crop in commodity_lower for crop in ["groundnut", "sesame", "mustard"]):
            return "Oil Seeds"
        else:
            return "Others"

    def _get_fallback_market_info(self, location: str) -> Dict[str, Any]:
        """Provide fallback market information when the website is down"""
        fallback_data = {
            "location": location,
            "status": "fallback_data",
            "message": "Using fallback market information due to website issues",
            "data_source": "fallback_estimate",
            "last_updated": "unknown",
            "note": "This is estimated data. For accurate prices, check the Karnataka government website directly.",
            "markets": {
                "General APMC": {
                    "commodity": "Various",
                    "status": "Market operational",
                    "note": "Contact market directly for current prices"
                }
            },
            "suggestions": [
                "Visit the APMC market directly for real-time prices",
                "Check local newspapers for daily price updates",
                "Contact local agricultural extension office",
                "Use other government price portals if available"
            ]
        }
        return fallback_data

    async def get_market_insights_for_feed(
        self, 
        location: str = "Karnataka",
        user_profile: str = "farmer"
    ) -> Dict[str, Any]:
        """
        Get market insights specifically formatted for the feed service
        
        Args:
            location: Location for market data
            user_profile: User profile for personalized insights
            
        Returns:
            Dictionary formatted for feed service integration
        """
        try:
            # Get market data with insights
            market_data = await self.get_prices_by_location(location, user_profile=user_profile)
            
            if market_data.get("status") != "success":
                return {
                    "type": "market_insights",
                    "status": "error",
                    "message": "Unable to fetch market data",
                    "data": None
                }
            
            # Extract key insights for feed
            ai_insights = market_data.get("ai_insights", {})
            insights = ai_insights.get("insights", [])
            
            # Format insights for feed display
            feed_insights = []
            for insight in insights:
                if insight.get("type") == "price_trends":
                    feed_insights.append({
                        "title": "Market Price Trends",
                        "summary": insight.get("summary", ""),
                        "key_points": [
                            f"Average Price: ₹{insight.get('statistics', {}).get('average_price', 0)}/quintal",
                            f"Price Range: ₹{insight.get('statistics', {}).get('price_range', 0)}",
                            f"High Value Crops: {len(insight.get('high_value_crops', []))} identified"
                        ],
                        "recommendation": insight.get("recommendation", ""),
                        "priority": "high" if "high_value_crops" in str(insight) else "medium"
                    })
                    
                elif insight.get("type") == "timing_analysis":
                    feed_insights.append({
                        "title": "Best Market Timing",
                        "summary": insight.get("timing_recommendation", ""),
                        "key_points": [
                            f"Current Month: {insight.get('current_month', '')}",
                            f"Recommended Action: {insight.get('action', '')}",
                            f"Profile: {user_profile.title()}"
                        ],
                        "recommendation": f"Best time to {insight.get('action', '')} based on seasonal patterns",
                        "priority": "medium"
                    })
                    
                elif insight.get("type") == "arbitrage_analysis":
                    opportunities = insight.get("opportunities", [])
                    if opportunities:
                        feed_insights.append({
                            "title": "Trading Opportunities",
                            "summary": f"Found {len(opportunities)} arbitrage opportunities",
                            "key_points": [
                                f"Top Opportunity: {opportunities[0].get('commodity', '')}",
                                f"Price Difference: ₹{opportunities[0].get('price_difference', 0)}",
                                f"Total Opportunities: {len(opportunities)}"
                            ],
                            "recommendation": insight.get("recommendation", ""),
                            "priority": "high"
                        })
            
            return {
                "type": "market_insights",
                "status": "success",
                "location": location,
                "user_profile": user_profile,
                "total_insights": len(feed_insights),
                "insights": feed_insights,
                "market_summary": {
                    "total_commodities": market_data.get("total_records", 0),
                    "data_source": market_data.get("data_source", ""),
                    "last_updated": market_data.get("date", "")
                },
                "feed_ready": True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating market insights for feed: {e}")
            return {
                "type": "market_insights",
                "status": "error",
                "message": f"Failed to generate insights: {str(e)}",
                "data": None
            }


# Global instance
karnataka_tool = KarnatakaMarketTool()
