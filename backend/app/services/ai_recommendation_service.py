"""
AI-Powered Real-Time Crop Recommendation Service

This service provides intelligent, context-aware farming recommendations by:
1. Analyzing real-time weather conditions
2. Monitoring market prices and trends
3. Assessing soil health and conditions
4. Tracking crop growth stages
5. Generating personalized action items

The system uses LLM integration to provide natural language recommendations
and prioritizes actions based on urgency and impact.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

# Import existing services
from app.services.open_meteo import OpenMeteoService
from app.services.karnataka_market_tool import karnataka_tool
from app.services.soil_health_service import SoilHealthService
from app.services.crop_tracking_service import CropTrackingService
from app.services.risk_assessment_service import RiskAssessmentService

# Import LLM integration
from app.chat.agent import ChatAgent

logger = logging.getLogger(__name__)

class RecommendationPriority(Enum):
    CRITICAL = "critical"      # Immediate action required (e.g., pest outbreak)
    HIGH = "high"             # Action needed within 24 hours
    MEDIUM = "medium"         # Action needed within 3 days
    LOW = "low"               # Informational or planning

class RecommendationType(Enum):
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PEST_CONTROL = "pest_control"
    HARVEST_TIMING = "harvest_timing"
    MARKET_ACTION = "market_action"
    WEATHER_ADAPTATION = "weather_adaptation"
    SOIL_IMPROVEMENT = "soil_improvement"
    CROP_PROTECTION = "crop_protection"

class AIRecommendation:
    def __init__(
        self,
        recommendation_id: str,
        title: str,
        description: str,
        recommendation_type: RecommendationType,
        priority: RecommendationPriority,
        action_items: List[str],
        reasoning: str,
        expected_impact: str,
        urgency_hours: int,
        data_sources: Dict[str, Any],
        created_at: datetime,
        expires_at: Optional[datetime] = None
    ):
        self.recommendation_id = recommendation_id
        self.title = title
        self.description = description
        self.recommendation_type = recommendation_type
        self.priority = priority
        self.action_items = action_items
        self.reasoning = reasoning
        self.expected_impact = expected_impact
        self.urgency_hours = urgency_hours
        self.data_sources = data_sources
        self.created_at = created_at
        self.expires_at = expires_at

class AIRecommendationService:
    def __init__(self):
        self.weather_service = OpenMeteoService()
        self.market_tool = karnataka_tool
        self.soil_service = SoilHealthService()
        self.tracking_service = CropTrackingService()
        self.risk_service = RiskAssessmentService()
        self.chat_agent = ChatAgent()
        
        # Cache for recommendations to avoid duplicates
        self.recommendation_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
    async def generate_real_time_recommendations(
        self,
        client_id: str,
        location: Dict[str, float],  # {lat, lon}
        crop_cycles: List[Dict[str, Any]],
        include_weather: bool = True,
        include_market: bool = True,
        include_soil: bool = True
    ) -> List[AIRecommendation]:
        """
        Generate real-time AI-powered recommendations for a farmer
        
        This is the main method that orchestrates data collection,
        analysis, and recommendation generation.
        """
        try:
            logger.info(f"Generating real-time recommendations for client {client_id}")
            
            # Step 1: Collect real-time data from all sources
            data_sources = await self._collect_real_time_data(
                location, crop_cycles, include_weather, include_market, include_soil
            )
            
            # Step 2: Analyze data and identify opportunities/threats
            analysis_results = await self._analyze_farming_conditions(
                data_sources, crop_cycles
            )
            
            # Step 3: Generate AI-powered recommendations
            recommendations = await self._generate_ai_recommendations(
                analysis_results, data_sources, client_id
            )
            
            # Step 4: Prioritize and filter recommendations
            prioritized_recommendations = self._prioritize_recommendations(recommendations)
            
            logger.info(f"Generated {len(prioritized_recommendations)} recommendations")
            return prioritized_recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _collect_real_time_data(
        self,
        location: Dict[str, float],
        crop_cycles: List[Dict[str, Any]],
        include_weather: bool,
        include_market: bool,
        include_soil: bool
    ) -> Dict[str, Any]:
        """Collect real-time data from all available sources"""
        data_sources = {
            "timestamp": datetime.now(),
            "location": location,
            "crop_cycles": crop_cycles
        }
        
        # Collect weather data
        if include_weather:
            try:
                weather_data = await self.weather_service.get_current_weather(
                    location["lat"], location["lon"]
                )
                weather_forecast = await self.weather_service.get_weather_forecast(
                    location["lat"], location["lon"], days=3
                )
                data_sources["weather"] = {
                    "current": weather_data,
                    "forecast": weather_forecast
                }
                logger.info("Weather data collected successfully")
            except Exception as e:
                logger.warning(f"Failed to collect weather data: {e}")
                data_sources["weather"] = None
        
        # Collect market data for relevant crops
        if include_market and crop_cycles:
            try:
                market_data = {}
                for cycle in crop_cycles:
                    if cycle.get("crop") and cycle["crop"].get("nameEn"):
                        crop_name = cycle["crop"]["nameEn"].lower()
                        try:
                            crop_market_data = await self.market_tool.get_prices_by_commodity(
                                crop_name, user_profile="farmer"
                            )
                            market_data[crop_name] = crop_market_data
                        except Exception as e:
                            logger.warning(f"Failed to get market data for {crop_name}: {e}")
                
                data_sources["market"] = market_data
                logger.info("Market data collected successfully")
            except Exception as e:
                logger.warning(f"Failed to collect market data: {e}")
                data_sources["market"] = None
        
        # Collect soil data
        if include_soil and location.get("pincode"):
            try:
                soil_data = await self.soil_service.get_soil_health(location["pincode"])
                data_sources["soil"] = soil_data
                logger.info("Soil data collected successfully")
            except Exception as e:
                logger.warning(f"Failed to collect soil data: {e}")
                data_sources["soil"] = None
        
        return data_sources
    
    async def _analyze_farming_conditions(
        self,
        data_sources: Dict[str, Any],
        crop_cycles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze collected data to identify opportunities and threats"""
        analysis = {
            "weather_risks": [],
            "market_opportunities": [],
            "soil_issues": [],
            "crop_health_alerts": [],
            "optimal_timing": []
        }
        
        # Analyze weather conditions
        if data_sources.get("weather"):
            weather_analysis = self._analyze_weather_conditions(
                data_sources["weather"], crop_cycles
            )
            analysis["weather_risks"] = weather_analysis["risks"]
            analysis["optimal_timing"].extend(weather_analysis["optimal_timing"])
        
        # Analyze market conditions
        if data_sources.get("market"):
            market_analysis = self._analyze_market_conditions(
                data_sources["market"], crop_cycles
            )
            analysis["market_opportunities"] = market_analysis["opportunities"]
            analysis["optimal_timing"].extend(market_analysis["optimal_timing"])
        
        # Analyze soil conditions
        if data_sources.get("soil"):
            soil_analysis = self._analyze_soil_conditions(
                data_sources["soil"], crop_cycles
            )
            analysis["soil_issues"] = soil_analysis["issues"]
            analysis["optimal_timing"].extend(soil_analysis["optimal_timing"])
        
        # Analyze crop health and growth stages
        crop_analysis = self._analyze_crop_conditions(crop_cycles)
        analysis["crop_health_alerts"] = crop_analysis["alerts"]
        analysis["optimal_timing"].extend(crop_analysis["optimal_timing"])
        
        return analysis
    
    def _analyze_weather_conditions(
        self,
        weather_data: Dict[str, Any],
        crop_cycles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze weather data for farming implications"""
        analysis = {"risks": [], "optimal_timing": []}
        
        current_weather = weather_data.get("current", {})
        forecast = weather_data.get("forecast", {})
        
        # Check for immediate weather risks
        if current_weather.get("precipitation_mm", 0) > 20:
            analysis["risks"].append({
                "type": "heavy_rain",
                "severity": "high",
                "description": "Heavy rainfall detected - risk of waterlogging",
                "urgency_hours": 2
            })
        
        if current_weather.get("wind_speed_kmh", 0) > 25:
            analysis["risks"].append({
                "type": "high_wind",
                "severity": "medium",
                "description": "High wind speeds - protect young crops",
                "urgency_hours": 4
            })
        
        # Check forecast for planning
        if forecast.get("daily"):
            daily_forecast = forecast["daily"]
            for i, day in enumerate(daily_forecast):
                if day.get("precipitation_probability_max", 0) > 80:
                    analysis["optimal_timing"].append({
                        "action": "delay_irrigation",
                        "reason": f"High rain probability on day {i+1}",
                        "timing": f"Day {i+1}"
                    })
        
        return analysis
    
    def _analyze_market_conditions(
        self,
        market_data: Dict[str, Any],
        crop_cycles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze market data for optimal timing opportunities"""
        analysis = {"opportunities": [], "optimal_timing": []}
        
        for crop_name, crop_data in market_data.items():
            if isinstance(crop_data, dict):
                # Check for price trends
                if crop_data.get("price_trend") == "rising":
                    analysis["opportunities"].append({
                        "type": "harvest_timing",
                        "crop": crop_name,
                        "description": f"Prices for {crop_name} are rising - consider early harvest",
                        "urgency_hours": 72
                    })
                
                # Check for storage recommendations
                if crop_data.get("storage_availability") == "limited":
                    analysis["optimal_timing"].append({
                        "action": "immediate_sale",
                        "reason": f"Limited storage for {crop_name}",
                        "timing": "Within 24 hours"
                    })
        
        return analysis
    
    def _analyze_soil_conditions(
        self,
        soil_data: Dict[str, Any],
        crop_cycles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze soil data for improvement opportunities"""
        analysis = {"issues": [], "optimal_timing": []}
        
        if soil_data:
            # Check pH levels
            ph_level = soil_data.get("ph_level")
            if ph_level and (ph_level < 6.0 or ph_level > 7.5):
                analysis["issues"].append({
                    "type": "ph_imbalance",
                    "severity": "medium",
                    "description": f"pH level {ph_level} is outside optimal range (6.0-7.5)",
                    "urgency_hours": 168  # 1 week
                })
            
            # Check nutrient levels
            nitrogen = soil_data.get("nitrogen_n", 0)
            if nitrogen < 50:
                analysis["issues"].append({
                    "type": "low_nitrogen",
                    "severity": "high",
                    "description": "Low nitrogen levels - fertilization needed",
                    "urgency_hours": 48
                })
        
        return analysis
    
    def _analyze_crop_conditions(
        self,
        crop_cycles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze crop health and growth stages"""
        analysis = {"alerts": [], "optimal_timing": []}
        
        for cycle in crop_cycles:
            # Check for overdue tasks
            if cycle.get("tasks"):
                for task in cycle["tasks"]:
                    if task.get("status") == "pending" and task.get("dueDate"):
                        due_date = datetime.fromisoformat(task["dueDate"])
                        if due_date < datetime.now():
                            analysis["alerts"].append({
                                "type": "overdue_task",
                                "severity": "high",
                                "description": f"Task '{task.get('taskName', 'Unknown')}' is overdue",
                                "urgency_hours": 0,
                                "crop_cycle_id": cycle.get("id")
                            })
            
            # Check growth stage timing
            if cycle.get("currentStage"):
                stage = cycle["currentStage"]
                if stage in ["flowering", "fruiting"]:
                    analysis["optimal_timing"].append({
                        "action": "monitor_closely",
                        "reason": f"Crop is in {stage} stage - critical period",
                        "timing": "Daily monitoring"
                    })
        
        return analysis
    
    async def _generate_ai_recommendations(
        self,
        analysis_results: Dict[str, Any],
        data_sources: Dict[str, Any],
        client_id: str
    ) -> List[AIRecommendation]:
        """Generate AI-powered recommendations using LLM integration"""
        recommendations = []
        
        # Generate recommendations for each analysis category
        if analysis_results["weather_risks"]:
            weather_recs = await self._generate_weather_recommendations(
                analysis_results["weather_risks"], data_sources, client_id
            )
            recommendations.extend(weather_recs)
        
        if analysis_results["market_opportunities"]:
            market_recs = await self._generate_market_recommendations(
                analysis_results["market_opportunities"], data_sources, client_id
            )
            recommendations.extend(market_recs)
        
        if analysis_results["soil_issues"]:
            soil_recs = await self._generate_soil_recommendations(
                analysis_results["soil_issues"], data_sources, client_id
            )
            recommendations.extend(soil_recs)
        
        if analysis_results["crop_health_alerts"]:
            crop_recs = await self._generate_crop_recommendations(
                analysis_results["crop_health_alerts"], data_sources, client_id
            )
            recommendations.extend(crop_recs)
        
        return recommendations
    
    async def _generate_weather_recommendations(
        self,
        weather_risks: List[Dict[str, Any]],
        data_sources: Dict[str, Any],
        client_id: str
    ) -> List[AIRecommendation]:
        """Generate weather-specific recommendations"""
        recommendations = []
        
        for risk in weather_risks:
            # Create recommendation using LLM
            prompt = f"""
            As an agricultural expert, provide a recommendation for a farmer facing this weather risk:
            
            Risk: {risk['description']}
            Severity: {risk['severity']}
            Urgency: {risk['urgency_hours']} hours
            
            Current weather conditions: {json.dumps(data_sources.get('weather', {}), indent=2)}
            
            Provide:
            1. A clear title for the recommendation
            2. Detailed description of what to do
            3. Specific action items (numbered list)
            4. Reasoning behind the recommendation
            5. Expected impact of following the recommendation
            """
            
            try:
                # Use the chat agent to generate recommendation
                response = await self.chat_agent.agenerate_response(prompt)
                
                # Parse the response and create recommendation
                recommendation = AIRecommendation(
                    recommendation_id=f"weather_{risk['type']}_{datetime.now().timestamp()}",
                    title=f"Weather Alert: {risk['type'].replace('_', ' ').title()}",
                    description=response[:200] + "..." if len(response) > 200 else response,
                    recommendation_type=RecommendationType.WEATHER_ADAPTATION,
                    priority=RecommendationPriority.CRITICAL if risk['severity'] == 'high' else RecommendationPriority.HIGH,
                    action_items=self._extract_action_items(response),
                    reasoning=response,
                    expected_impact="Prevent crop damage and optimize resource use",
                    urgency_hours=risk['urgency_hours'],
                    data_sources={"weather": data_sources.get("weather")},
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=risk['urgency_hours'])
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Failed to generate LLM recommendation for weather risk: {e}")
                # Fallback to template-based recommendation
                fallback_rec = self._create_fallback_recommendation(risk, data_sources)
                if fallback_rec:
                    recommendations.append(fallback_rec)
        
        return recommendations
    
    async def _generate_market_recommendations(
        self,
        market_opportunities: List[Dict[str, Any]],
        data_sources: Dict[str, Any],
        client_id: str
    ) -> List[AIRecommendation]:
        """Generate market-specific recommendations"""
        recommendations = []
        
        for opportunity in market_opportunities:
            prompt = f"""
            As an agricultural market expert, provide a recommendation for a farmer based on this market opportunity:
            
            Opportunity: {opportunity['description']}
            Crop: {opportunity.get('crop', 'Unknown')}
            Urgency: {opportunity['urgency_hours']} hours
            
            Market data: {json.dumps(data_sources.get('market', {}), indent=2)}
            
            Provide:
            1. A clear title for the recommendation
            2. Detailed description of what to do
            3. Specific action items (numbered list)
            4. Reasoning behind the recommendation
            5. Expected impact of following the recommendation
            """
            
            try:
                response = await self.chat_agent.agenerate_response(prompt)
                
                recommendation = AIRecommendation(
                    recommendation_id=f"market_{opportunity['type']}_{datetime.now().timestamp()}",
                    title=f"Market Opportunity: {opportunity['type'].replace('_', ' ').title()}",
                    description=response[:200] + "..." if len(response) > 200 else response,
                    recommendation_type=RecommendationType.MARKET_ACTION,
                    priority=RecommendationPriority.HIGH,
                    action_items=self._extract_action_items(response),
                    reasoning=response,
                    expected_impact="Maximize profit through optimal market timing",
                    urgency_hours=opportunity['urgency_hours'],
                    data_sources={"market": data_sources.get("market")},
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=opportunity['urgency_hours'])
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Failed to generate LLM recommendation for market opportunity: {e}")
        
        return recommendations
    
    async def _generate_soil_recommendations(
        self,
        soil_issues: List[Dict[str, Any]],
        data_sources: Dict[str, Any],
        client_id: str
    ) -> List[AIRecommendation]:
        """Generate soil-specific recommendations"""
        recommendations = []
        
        for issue in soil_issues:
            prompt = f"""
            As a soil health expert, provide a recommendation for a farmer facing this soil issue:
            
            Issue: {issue['description']}
            Severity: {issue['severity']}
            Urgency: {issue['urgency_hours']} hours
            
            Soil data: {json.dumps(data_sources.get('soil', {}), indent=2)}
            
            Provide:
            1. A clear title for the recommendation
            2. Detailed description of what to do
            3. Specific action items (numbered list)
            4. Reasoning behind the recommendation
            5. Expected impact of following the recommendation
            """
            
            try:
                response = await self.chat_agent.agenerate_response(prompt)
                
                recommendation = AIRecommendation(
                    recommendation_id=f"soil_{issue['type']}_{datetime.now().timestamp()}",
                    title=f"Soil Health: {issue['type'].replace('_', ' ').title()}",
                    description=response[:200] + "..." if len(response) > 200 else response,
                    recommendation_type=RecommendationType.SOIL_IMPROVEMENT,
                    priority=RecommendationPriority.HIGH if issue['severity'] == 'high' else RecommendationPriority.MEDIUM,
                    action_items=self._extract_action_items(response),
                    reasoning=response,
                    expected_impact="Improve soil health and crop productivity",
                    urgency_hours=issue['urgency_hours'],
                    data_sources={"soil": data_sources.get("soil")},
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=issue['urgency_hours'])
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Failed to generate LLM recommendation for soil issue: {e}")
        
        return recommendations
    
    async def _generate_crop_recommendations(
        self,
        crop_alerts: List[Dict[str, Any]],
        data_sources: Dict[str, Any],
        client_id: str
    ) -> List[AIRecommendation]:
        """Generate crop-specific recommendations"""
        recommendations = []
        
        for alert in crop_alerts:
            prompt = f"""
            As a crop management expert, provide a recommendation for a farmer facing this crop issue:
            
            Alert: {alert['description']}
            Severity: {alert.get('severity', 'medium')}
            Urgency: {alert['urgency_hours']} hours
            
            Provide:
            1. A clear title for the recommendation
            2. Detailed description of what to do
            3. Specific action items (numbered list)
            4. Reasoning behind the recommendation
            5. Expected impact of following the recommendation
            """
            
            try:
                response = await self.chat_agent.agenerate_response(prompt)
                
                recommendation = AIRecommendation(
                    recommendation_id=f"crop_{alert['type']}_{datetime.now().timestamp()}",
                    title=f"Crop Alert: {alert['type'].replace('_', ' ').title()}",
                    description=response[:200] + "..." if len(response) > 200 else response,
                    recommendation_type=RecommendationType.CROP_PROTECTION,
                    priority=RecommendationPriority.CRITICAL if alert.get('severity') == 'high' else RecommendationPriority.HIGH,
                    action_items=self._extract_action_items(response),
                    reasoning=response,
                    expected_impact="Maintain crop health and optimize growth",
                    urgency_hours=alert['urgency_hours'],
                    data_sources={"crop_cycles": data_sources.get("crop_cycles")},
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=alert['urgency_hours'])
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Failed to generate LLM recommendation for crop alert: {e}")
        
        return recommendations
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from LLM response"""
        action_items = []
        
        # Simple extraction - look for numbered items
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # Clean up the action item
                clean_item = line.lstrip('0123456789.•- ').strip()
                if clean_item and len(clean_item) > 10:  # Minimum meaningful length
                    action_items.append(clean_item)
        
        # If no numbered items found, create generic ones
        if not action_items:
            action_items = [
                "Review the current situation",
                "Implement the recommended actions",
                "Monitor the results",
                "Adjust strategy if needed"
            ]
        
        return action_items[:5]  # Limit to 5 action items
    
    def _create_fallback_recommendation(
        self,
        risk: Dict[str, Any],
        data_sources: Dict[str, Any]
    ) -> Optional[AIRecommendation]:
        """Create a fallback recommendation when LLM fails"""
        try:
            if risk['type'] == 'heavy_rain':
                return AIRecommendation(
                    recommendation_id=f"fallback_weather_{risk['type']}_{datetime.now().timestamp()}",
                    title="Heavy Rainfall Alert",
                    description="Immediate action required to prevent waterlogging and crop damage",
                    recommendation_type=RecommendationType.WEATHER_ADAPTATION,
                    priority=RecommendationPriority.CRITICAL,
                    action_items=[
                        "Stop irrigation immediately",
                        "Check drainage systems",
                        "Protect vulnerable crops with covers",
                        "Monitor water levels in fields"
                    ],
                    reasoning="Heavy rainfall can cause waterlogging which damages crop roots and reduces yield",
                    expected_impact="Prevent crop damage and maintain soil health",
                    urgency_hours=risk['urgency_hours'],
                    data_sources={"weather": data_sources.get("weather")},
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=risk['urgency_hours'])
                )
        except Exception as e:
            logger.warning(f"Failed to create fallback recommendation: {e}")
        
        return None
    
    def _prioritize_recommendations(
        self,
        recommendations: List[AIRecommendation]
    ) -> List[AIRecommendation]:
        """Prioritize recommendations based on urgency and impact"""
        # Sort by priority (critical > high > medium > low)
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3
        }
        
        sorted_recommendations = sorted(
            recommendations,
            key=lambda r: (priority_order[r.priority], r.urgency_hours)
        )
        
        # Limit to top 10 recommendations to avoid overwhelming the user
        return sorted_recommendations[:10]
    
    async def get_recommendations_for_client(
        self,
        client_id: str,
        max_recommendations: int = 10
    ) -> List[AIRecommendation]:
        """Get cached recommendations for a client"""
        cache_key = f"recommendations_{client_id}"
        
        if cache_key in self.recommendation_cache:
            cached_data = self.recommendation_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_data["recommendations"][:max_recommendations]
        
        return []
    
    def clear_cache(self, client_id: Optional[str] = None):
        """Clear recommendation cache"""
        if client_id:
            cache_key = f"recommendations_{client_id}"
            if cache_key in self.recommendation_cache:
                del self.recommendation_cache[cache_key]
        else:
            self.recommendation_cache.clear()

# Global instance
ai_recommendation_service = AIRecommendationService()
