"""
Crop Planning Engine Service
Intelligent crop planning using collected data and AI-powered recommendations
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.output_parser import StrOutputParser

from app.services.data_collection_coordinator import DataCollectionCoordinator
from app.services.soil_health_service import SoilHealthData
from app.services.crop_calendar_service import CropCalendar, Season
from app.services.scheme_matching_service import SchemeMatch
from app.services.real_data_integration_service import RealDataIntegrationService, RealTimeWeatherData, RealTimeMarketData, RealTimeSoilData
from app.config import settings

logger = logging.getLogger(__name__)

class PlanStatus(Enum):
    """Status of crop planning"""
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CropRecommendation:
    """AI-generated crop recommendation"""
    crop_name: str
    crop_variety: str
    confidence_score: float
    reasoning: List[str]
    expected_yield_per_acre: float
    market_demand_score: float
    risk_level: RiskLevel
    soil_suitability_score: float
    climate_suitability_score: float
    financial_viability_score: float

@dataclass
class PlantingSchedule:
    """Detailed planting schedule"""
    optimal_planting_date: date
    planting_window_start: date
    planting_window_end: date
    critical_factors: List[str]
    preparation_tasks: List[str]
    weather_considerations: List[str]

@dataclass
class ResourceRequirement:
    """Resource requirements for crop cycle"""
    seeds_kg_per_acre: float
    fertilizers_kg_per_acre: Dict[str, float]
    pesticides_liters_per_acre: float
    water_requirement_mm: float
    labor_days_per_acre: float
    equipment_hours_per_acre: float
    estimated_cost_per_acre: float

@dataclass
class CropPlan:
    """Complete crop planning document"""
    plan_id: str
    farmer_id: str
    crop_name: str
    crop_variety: str
    season: Season
    area_acres: float
    status: PlanStatus
    
    # Planning data
    recommendation: CropRecommendation
    planting_schedule: PlantingSchedule
    resource_requirements: ResourceRequirement
    
    # Integration data
    soil_health_data: Optional[SoilHealthData]
    crop_calendar: Optional[CropCalendar]
    eligible_schemes: List[SchemeMatch]
    
    # Financial planning
    estimated_investment: float
    expected_revenue: float
    subsidy_benefits: float
    net_profit_estimate: float
    
    # Risk assessment
    risk_factors: List[str]
    mitigation_strategies: List[str]
    insurance_recommendations: List[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str
    approval_status: str

class CropPlanningEngine:
    """AI-powered crop planning engine"""
    
    def __init__(self):
        self.data_coordinator = DataCollectionCoordinator()
        self.real_data_service = RealDataIntegrationService()
        self.plan_cache = {}
        self.recommendation_cache = {}
        
        # Planning parameters
        self.min_confidence_score = 0.7
        self.max_risk_level = RiskLevel.HIGH
        self.min_soil_suitability = 0.6
        self.min_climate_suitability = 0.7
        
        # Initialize LangChain LLM
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.3,  # Lower temperature for more consistent agricultural advice
                max_output_tokens=2048
            )
            self.llm_available = True
            logger.info("LangChain LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize LangChain LLM: {e}")
            self.llm_available = False
            self.llm = None
        
        # Initialize LangChain prompts
        self._initialize_langchain_prompts()
        
    def _initialize_langchain_prompts(self):
        """Initialize LangChain prompt templates for different agricultural tasks"""
        try:
            # Crop recommendation prompt
            self.crop_recommendation_prompt = ChatPromptTemplate.from_template("""
You are an expert agricultural advisor with deep knowledge of Indian farming practices, soil science, and crop management.

Farmer Profile:
- Location: {location}
- Farm Size: {farm_size} acres
- Experience: {experience_years} years
- Irrigation Type: {irrigation_type}
- Soil Type: {soil_type}
- Language Preference: {language}

Soil Health Data:
- pH Level: {ph_level}
- Organic Carbon: {organic_carbon}%
- Nitrogen (N): {nitrogen_n} kg/ha
- Phosphorus (P): {phosphorus_p} kg/ha
- Potassium (K): {potassium_k} kg/ha

Target Season: {season}
Available Crops: {available_crops}

Based on this information, provide a detailed crop recommendation analysis. Consider:
1. Soil suitability for each crop
2. Climate and seasonal factors
3. Market demand and profitability
4. Farmer's experience level
5. Local agricultural practices
6. Risk factors and mitigation strategies

Provide your analysis in the following JSON format:
{{
    "crop_name": "crop name",
    "crop_variety": "recommended variety",
    "confidence_score": 0.85,
    "reasoning": ["reason 1", "reason 2", "reason 3"],
    "expected_yield_per_acre": 25.5,
    "market_demand_score": 0.8,
    "risk_level": "medium",
    "soil_suitability_score": 0.8,
    "climate_suitability_score": 0.9,
    "financial_viability_score": 0.85,
    "detailed_analysis": "comprehensive explanation of why this crop is recommended",
    "specific_recommendations": ["specific action 1", "specific action 2"],
    "local_best_practices": ["local practice 1", "local practice 2"]
}}
""")

            # Planting schedule prompt
            self.planting_schedule_prompt = ChatPromptTemplate.from_template("""
You are an expert agricultural planner specializing in optimal planting schedules for Indian farmers.

Crop: {crop_name}
Variety: {crop_variety}
Season: {season}
Location: {location}
Soil Type: {soil_type}
Irrigation: {irrigation_type}

Current Weather Conditions:
- Temperature: {temperature}
- Humidity: {humidity}
- Rainfall: {rainfall}
- Wind: {wind_speed}

Based on this information, create an optimal planting schedule considering:
1. Weather patterns and forecasts
2. Soil moisture requirements
3. Crop-specific growth requirements
4. Local agricultural calendar
5. Risk mitigation strategies

Provide your schedule in the following JSON format:
{{
    "optimal_planting_date": "YYYY-MM-DD",
    "planting_window_start": "YYYY-MM-DD",
    "planting_window_end": "YYYY-MM-DD",
    "critical_factors": ["factor 1", "factor 2"],
    "preparation_tasks": ["task 1", "task 2"],
    "weather_considerations": ["consideration 1", "consideration 2"],
    "soil_preparation": ["preparation step 1", "preparation step 2"],
    "risk_mitigation": ["mitigation strategy 1", "mitigation strategy 2"]
}}
""")

            # Risk assessment prompt
            self.risk_assessment_prompt = ChatPromptTemplate.from_template("""
You are an agricultural risk assessment expert specializing in Indian farming conditions.

Crop: {crop_name}
Variety: {crop_variety}
Season: {season}
Location: {location}
Farm Size: {farm_size} acres
Experience: {experience_years} years

Current Conditions:
- Soil Suitability: {soil_suitability_score}
- Climate Suitability: {climate_suitability_score}
- Market Demand: {market_demand_score}
- Weather Forecast: {weather_forecast}

Based on this information, assess the risks and provide mitigation strategies. Consider:
1. Weather-related risks
2. Soil and nutrient risks
3. Pest and disease risks
4. Market and financial risks
5. Operational risks based on farm size and experience

Provide your assessment in the following JSON format:
{{
    "risk_factors": ["risk 1", "risk 2", "risk 3"],
    "risk_levels": {{"risk_1": "high", "risk_2": "medium", "risk_3": "low"}},
    "mitigation_strategies": ["strategy 1", "strategy 2", "strategy 3"],
    "insurance_recommendations": ["insurance 1", "insurance 2"],
    "monitoring_checklist": ["check 1", "check 2", "check 3"],
    "early_warning_signs": ["sign 1", "sign 2"],
    "contingency_plans": ["plan 1", "plan 2"],
    "expert_consultation": ["when to consult expert 1", "when to consult expert 2"]
}}
""")

            # Smart checklist prompt
            self.smart_checklist_prompt = ChatPromptTemplate.from_template("""
You are an expert agricultural task planner creating personalized checklists for Indian farmers.

Crop: {crop_name}
Variety: {crop_variety}
Planting Date: {planting_date}
Location: {location}
Farm Size: {farm_size} acres
Experience: {experience_years} years
Irrigation: {irrigation_type}
Language: {language}

Current Conditions:
- Soil Health: {soil_health_summary}
- Weather: {weather_summary}
- Market: {market_summary}

Create a comprehensive, personalized task checklist that considers:
1. Crop-specific growth requirements
2. Farmer's experience level (beginner/intermediate/expert)
3. Farm size and resource availability
4. Local weather patterns and seasonal factors
5. Soil conditions and improvement needs
6. Market timing and optimization opportunities
7. Risk mitigation and monitoring tasks

Provide your checklist in the following JSON format:
{{
    "tasks": [
        {{
            "task_name": "task name",
            "task_description": "detailed description",
            "task_type": "observation|action|measurement|planning",
            "due_date": "YYYY-MM-DD",
            "priority": "critical|high|medium|low",
            "experience_level": "beginner|intermediate|expert",
            "resource_requirements": ["resource 1", "resource 2"],
            "success_criteria": "how to know task is complete",
            "local_tips": ["local tip 1", "local tip 2"],
            "risk_mitigation": "how this task reduces risks"
        }}
    ],
    "overall_strategy": "high-level approach to crop management",
    "key_milestones": ["milestone 1", "milestone 2"],
    "success_indicators": ["indicator 1", "indicator 2"]
}}
""")

            logger.info("LangChain prompts initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LangChain prompts: {e}")
            self.crop_recommendation_prompt = None
            self.planting_schedule_prompt = None
            self.risk_assessment_prompt = None
            self.smart_checklist_prompt = None
        
    async def generate_crop_plan(
        self,
        farmer_profile: Dict[str, Any],
        target_crop: Optional[str] = None,
        target_area: Optional[float] = None,
        target_season: Optional[Season] = None,
        force_refresh: bool = False
    ) -> CropPlan:
        """
        Generate comprehensive crop plan for a farmer
        
        Args:
            farmer_profile: Farmer's profile and preferences
            target_crop: Specific crop to plan for (optional)
            target_area: Target area in acres (optional)
            target_season: Target season (optional)
            force_refresh: Force refresh of data
            
        Returns:
            Complete CropPlan object
        """
        try:
            logger.info(f"Generating crop plan for farmer {farmer_profile.get('client_id', 'unknown')}")
            
            # Collect comprehensive farmer data using real data sources
            farmer_data = await self.real_data_service.get_comprehensive_farmer_data(
                farmer_profile, force_refresh
            )
            
            # Generate crop recommendations
            recommendations = await self._generate_crop_recommendations(
                farmer_data, target_crop, target_season
            )
            
            if not recommendations:
                raise ValueError("No suitable crop recommendations found")
            
            # Select best recommendation
            best_recommendation = self._select_best_recommendation(recommendations)
            
            # Generate planting schedule
            planting_schedule = await self._generate_planting_schedule(
                best_recommendation, farmer_data, target_season
            )
            
            # Calculate resource requirements
            resource_requirements = await self._calculate_resource_requirements(
                best_recommendation, farmer_data, target_area or farmer_profile.get('farm_size', 1.0)
            )
            
            # Perform financial planning
            financial_plan = await self._perform_financial_planning(
                best_recommendation, resource_requirements, farmer_data
            )
            
            # Assess risks and mitigation
            risk_assessment = await self._assess_risks_and_mitigation(
                best_recommendation, farmer_data, planting_schedule
            )
            
            # Create comprehensive plan
            crop_plan = CropPlan(
                plan_id=f"plan_{farmer_profile.get('client_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                farmer_id=farmer_profile.get('client_id', 'unknown'),
                crop_name=best_recommendation.crop_name,
                crop_variety=best_recommendation.crop_variety,
                season=target_season or Season.KHARIF,
                area_acres=target_area or farmer_profile.get('farm_size', 1.0),
                status=PlanStatus.DRAFT,
                recommendation=best_recommendation,
                planting_schedule=planting_schedule,
                resource_requirements=resource_requirements,
                soil_health_data=farmer_data.soil_health,
                crop_calendar=next((cal for cal in farmer_data.crop_calendars 
                                  if cal.crop_name.lower() == best_recommendation.crop_name.lower()), None),
                eligible_schemes=farmer_data.eligible_schemes,
                estimated_investment=financial_plan['estimated_investment'],
                expected_revenue=financial_plan['expected_revenue'],
                subsidy_benefits=financial_plan['subsidy_benefits'],
                net_profit_estimate=financial_plan['net_profit_estimate'],
                risk_factors=risk_assessment['risk_factors'],
                mitigation_strategies=risk_assessment['mitigation_strategies'],
                insurance_recommendations=risk_assessment['insurance_recommendations'],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by="AI Planning Engine",
                approval_status="pending"
            )
            
            # Cache the plan
            self._cache_plan(crop_plan.plan_id, crop_plan)
            
            logger.info(f"Crop plan generated successfully: {crop_plan.plan_id}")
            return crop_plan
            
        except Exception as e:
            logger.error(f"Error generating crop plan: {e}")
            raise
    
    async def _generate_crop_recommendations(
        self, 
        farmer_data: Any, 
        target_crop: Optional[str], 
        target_season: Optional[Season]
    ) -> List[CropRecommendation]:
        """Generate crop recommendations based on farmer data"""
        try:
            recommendations = []
            
            # Get available crops for the season
            season = target_season or Season.KHARIF
            available_crops = await self._get_available_crops_for_season(
                farmer_data, season
            )
            
            # Filter by target crop if specified
            if target_crop:
                available_crops = [crop for crop in available_crops if target_crop.lower() in crop.lower()]
            
            # Generate recommendations for each available crop
            for crop_name in available_crops[:5]:  # Limit to top 5
                recommendation = await self._analyze_crop_suitability(
                    crop_name, farmer_data, season
                )
                if recommendation and recommendation.confidence_score >= self.min_confidence_score:
                    recommendations.append(recommendation)
            
            # Sort by confidence score
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating crop recommendations: {e}")
            return []
    
    async def _analyze_crop_suitability(
        self, 
        crop_name: str, 
        farmer_data: Any, 
        season: Season
    ) -> Optional[CropRecommendation]:
        """Analyze suitability of a specific crop using LangChain LLM"""
        try:
            # Get crop calendar
            crop_calendar = next((cal for cal in farmer_data.crop_calendars 
                                if cal.crop_name.lower() == crop_name.lower()), None)
            
            if not crop_calendar:
                return None
            
            # Analyze soil suitability
            soil_suitability = self._analyze_soil_suitability(crop_name, farmer_data.soil_health)
            
            # Analyze climate suitability
            climate_suitability = self._analyze_climate_suitability(crop_calendar, season)
            
            # Analyze market demand using real data
            market_demand = await self._analyze_market_demand(crop_name, season, farmer_data.location)
            
            # Use LangChain LLM for enhanced analysis if available
            if self.llm_available and self.crop_recommendation_prompt:
                try:
                    # Prepare context for LLM
                    llm_context = await self._prepare_llm_context_for_crop_analysis(
                        crop_name, farmer_data, season, soil_suitability, climate_suitability, market_demand
                    )
                    
                    # Generate LLM-enhanced recommendation
                    llm_recommendation = await self._generate_llm_crop_recommendation(llm_context)
                    
                    if llm_recommendation:
                        # Merge LLM insights with calculated scores
                        return await self._merge_llm_and_calculated_recommendation(
                            llm_recommendation, crop_name, crop_calendar, soil_suitability, 
                            climate_suitability, market_demand
                        )
                        
                except Exception as e:
                    logger.warning(f"LLM crop analysis failed, falling back to rule-based: {e}")
            
            # Fallback to rule-based analysis
            confidence_score = self._calculate_confidence_score(
                soil_suitability, climate_suitability, market_demand
            )
            
            # Assess risk level
            risk_level = self._assess_risk_level(soil_suitability, climate_suitability)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                crop_name, soil_suitability, climate_suitability, market_demand
            )
            
            return CropRecommendation(
                crop_name=crop_name,
                crop_variety=crop_calendar.crop_variety if crop_calendar else "Standard",
                confidence_score=confidence_score,
                reasoning=reasoning,
                expected_yield_per_acre=self._estimate_yield(crop_name, soil_suitability),
                market_demand_score=market_demand,
                risk_level=risk_level,
                soil_suitability_score=soil_suitability,
                climate_suitability_score=climate_suitability,
                financial_viability_score=self._calculate_financial_viability(
                    crop_name, market_demand, risk_level
                )
            )
            
        except Exception as e:
            logger.error(f"Error analyzing crop suitability: {e}")
            return None
    
    def _analyze_soil_suitability(self, crop_name: str, soil_health: Optional[SoilHealthData]) -> float:
        """Analyze soil suitability for a crop using real soil data"""
        try:
            if not soil_health:
                return 0.5  # Neutral score if no soil data
            
            # Crop-specific soil requirements
            crop_soil_requirements = {
                "rice": {"ph_min": 5.5, "ph_max": 7.5, "organic_carbon_min": 0.5},
                "wheat": {"ph_min": 6.0, "ph_max": 7.5, "organic_carbon_min": 0.4},
                "maize": {"ph_min": 5.5, "ph_max": 7.5, "organic_carbon_min": 0.5},
                "cotton": {"ph_min": 5.5, "ph_max": 8.5, "organic_carbon_min": 0.3},
                "sugarcane": {"ph_min": 6.0, "ph_max": 8.0, "organic_carbon_min": 0.4}
            }
            
            requirements = crop_soil_requirements.get(crop_name.lower(), {
                "ph_min": 6.0, "ph_max": 7.5, "organic_carbon_min": 0.4
            })
            
            # Check pH suitability
            ph_score = 0.0
            if requirements["ph_min"] <= soil_health.ph_level <= requirements["ph_max"]:
                ph_score = 1.0
            else:
                ph_score = max(0.0, 1.0 - abs(soil_health.ph_level - 7.0) / 2.0)
            
            # Check organic carbon
            oc_score = min(1.0, soil_health.organic_carbon / requirements["organic_carbon_min"])
            
            # Check NPK levels
            npk_score = self._calculate_npk_score(soil_health)
            
            # Calculate overall soil suitability
            soil_suitability = (ph_score * 0.4 + oc_score * 0.3 + npk_score * 0.3)
            
            return min(1.0, max(0.0, soil_suitability))
            
        except Exception as e:
            logger.error(f"Error analyzing soil suitability: {e}")
            return 0.5
    
    def _calculate_npk_score(self, soil_health: SoilHealthData) -> float:
        """Calculate NPK score based on soil health data"""
        try:
            # Ideal NPK levels (kg/ha)
            ideal_n = 280.0
            ideal_p = 140.0
            ideal_k = 140.0
            
            # Calculate scores
            n_score = min(1.0, soil_health.nitrogen_n / ideal_n)
            p_score = min(1.0, soil_health.phosphorus_p / ideal_p)
            k_score = min(1.0, soil_health.potassium_k / ideal_k)
            
            # Weighted average
            npk_score = (n_score * 0.4 + p_score * 0.35 + k_score * 0.25)
            
            return npk_score
            
        except Exception as e:
            logger.error(f"Error calculating NPK score: {e}")
            return 0.5
    
    def _analyze_climate_suitability(self, crop_calendar: CropCalendar, season: Season) -> float:
        """Analyze climate suitability for a crop"""
        try:
            # Check if crop calendar matches season
            if crop_calendar.season != season:
                return 0.3  # Lower score for season mismatch
            
            # Check planting window timing
            current_date = datetime.now().date()
            if crop_calendar.optimal_planting_start and crop_calendar.optimal_planting_end:
                if (crop_calendar.optimal_planting_start <= current_date <= crop_calendar.optimal_planting_end):
                    timing_score = 1.0
                elif (current_date < crop_calendar.optimal_planting_start):
                    days_until = (crop_calendar.optimal_planting_start - current_date).days
                    timing_score = max(0.5, 1.0 - (days_until / 30.0))
                else:
                    timing_score = 0.3
            else:
                timing_score = 0.7
            
            # Check duration suitability
            duration_score = 1.0
            if crop_calendar.total_duration_days > 180:  # Very long duration
                duration_score = 0.8
            elif crop_calendar.total_duration_days < 90:  # Very short duration
                duration_score = 0.9
            
            # Calculate overall climate suitability
            climate_suitability = (timing_score * 0.7 + duration_score * 0.3)
            
            return min(1.0, max(0.0, climate_suitability))
            
        except Exception as e:
            logger.error(f"Error analyzing climate suitability: {e}")
            return 0.7
    
    async def _analyze_market_demand(self, crop_name: str, season: Season, location: Dict[str, float] = None) -> float:
        """Analyze market demand for a crop using real market data"""
        try:
            # Get real market data if location is available
            if location and location.get('lat') and location.get('lng'):
                try:
                    # Get real-time market data
                    market_data = await self.real_data_service.get_real_time_market_data(
                        crop_name, 
                        state=location.get('state', 'Karnataka')
                    )
                    
                    if market_data:
                        # Calculate demand score based on real market data
                        prices = [m.modal_price for m in market_data if m.modal_price > 0]
                        if prices:
                            avg_price = sum(prices) / len(prices)
                            # Higher prices indicate higher demand
                            demand_score = min(1.0, avg_price / 5000.0)  # Normalize to 0-1 scale
                            return demand_score
                except Exception as e:
                    logger.warning(f"Failed to fetch real market data: {e}")
            
            # Fallback to seasonal patterns if real data unavailable
            market_patterns = {
                "rice": {"kharif": 0.9, "rabi": 0.8, "zaid": 0.7},
                "wheat": {"kharif": 0.6, "rabi": 0.9, "zaid": 0.5},
                "maize": {"kharif": 0.8, "rabi": 0.7, "zaid": 0.6},
                "cotton": {"kharif": 0.9, "rabi": 0.4, "zaid": 0.3},
                "sugarcane": {"kharif": 0.8, "rabi": 0.7, "zaid": 0.6}
            }
            
            demand_score = market_patterns.get(crop_name.lower(), {}).get(season.value, 0.7)
            
            return demand_score
            
        except Exception as e:
            logger.error(f"Error analyzing market demand: {e}")
            return 0.7
    
    def _calculate_confidence_score(
        self, 
        soil_suitability: float, 
        climate_suitability: float, 
        market_demand: float
    ) -> float:
        """Calculate overall confidence score"""
        try:
            # Weighted average
            confidence = (
                soil_suitability * 0.4 +
                climate_suitability * 0.35 +
                market_demand * 0.25
            )
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    def _assess_risk_level(self, soil_suitability: float, climate_suitability: float) -> RiskLevel:
        """Assess risk level based on suitability scores"""
        try:
            avg_suitability = (soil_suitability + climate_suitability) / 2.0
            
            if avg_suitability >= 0.8:
                return RiskLevel.LOW
            elif avg_suitability >= 0.6:
                return RiskLevel.MEDIUM
            elif avg_suitability >= 0.4:
                return RiskLevel.HIGH
            else:
                return RiskLevel.CRITICAL
                
        except Exception as e:
            logger.error(f"Error assessing risk level: {e}")
            return RiskLevel.MEDIUM
    
    def _estimate_yield(self, crop_name: str, soil_suitability: float) -> float:
        """Estimate expected yield per acre"""
        try:
            # Base yields per acre (quintals)
            base_yields = {
                "rice": 25.0,
                "wheat": 20.0,
                "maize": 30.0,
                "cotton": 15.0,
                "sugarcane": 400.0
            }
            
            base_yield = base_yields.get(crop_name.lower(), 20.0)
            
            # Adjust based on soil suitability
            adjusted_yield = base_yield * (0.5 + soil_suitability * 0.5)
            
            return adjusted_yield
            
        except Exception as e:
            logger.error(f"Error estimating yield: {e}")
            return 20.0
    
    def _calculate_financial_viability(
        self, 
        crop_name: str, 
        market_demand: float, 
        risk_level: RiskLevel
    ) -> float:
        """Calculate financial viability score"""
        try:
            # Base financial score
            base_score = market_demand
            
            # Adjust for risk level
            risk_adjustments = {
                RiskLevel.LOW: 1.0,
                RiskLevel.MEDIUM: 0.9,
                RiskLevel.HIGH: 0.7,
                RiskLevel.CRITICAL: 0.5
            }
            
            risk_adjustment = risk_adjustments.get(risk_level, 0.8)
            
            # Calculate final viability
            viability = base_score * risk_adjustment
            
            return min(1.0, max(0.0, viability))
            
        except Exception as e:
            logger.error(f"Error calculating financial viability: {e}")
            return 0.7
    
    def _generate_reasoning(
        self, 
        crop_name: str, 
        soil_suitability: float, 
        climate_suitability: float, 
        market_demand: float
    ) -> List[str]:
        """Generate reasoning for recommendation"""
        try:
            reasoning = []
            
            # Soil reasoning
            if soil_suitability >= 0.8:
                reasoning.append("Excellent soil conditions for this crop")
            elif soil_suitability >= 0.6:
                reasoning.append("Good soil conditions with minor considerations")
            else:
                reasoning.append("Soil conditions may require improvement")
            
            # Climate reasoning
            if climate_suitability >= 0.8:
                reasoning.append("Optimal climate timing for planting")
            elif climate_suitability >= 0.6:
                reasoning.append("Suitable climate conditions")
            else:
                reasoning.append("Climate timing may not be optimal")
            
            # Market reasoning
            if market_demand >= 0.8:
                reasoning.append("High market demand expected")
            elif market_demand >= 0.6:
                reasoning.append("Moderate market demand")
            else:
                reasoning.append("Lower market demand expected")
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return ["Analysis completed with available data"]
    
    def _select_best_recommendation(self, recommendations: List[CropRecommendation]) -> CropRecommendation:
        """Select the best crop recommendation"""
        try:
            if not recommendations:
                raise ValueError("No recommendations available")
            
            # Sort by confidence score and select best
            best_recommendation = max(recommendations, key=lambda x: x.confidence_score)
            
            return best_recommendation
            
        except Exception as e:
            logger.error(f"Error selecting best recommendation: {e}")
            raise
    
    async def _generate_planting_schedule(
        self, 
        recommendation: CropRecommendation, 
        farmer_data: Any, 
        target_season: Optional[Season]
    ) -> PlantingSchedule:
        """Generate detailed planting schedule using real weather data and LangChain LLM"""
        try:
            # Get crop calendar
            crop_calendar = next((cal for cal in farmer_data.crop_calendars 
                                if cal.crop_name.lower() == recommendation.crop_name.lower()), None)
            
            # Get real-time weather data for better scheduling
            weather_data = None
            if farmer_data.location and farmer_data.location.get('lat') and farmer_data.location.get('lng'):
                try:
                    weather_data = await self.real_data_service.get_real_time_weather(
                        farmer_data.location['lat'], 
                        farmer_data.location['lng']
                    )
                    
                    # Get weather forecast for planning
                    weather_forecast = await self.real_data_service.get_weather_forecast(
                        farmer_data.location['lat'], 
                        farmer_data.location['lng'], 
                        days=14
                    )
                except Exception as e:
                    logger.warning(f"Failed to fetch real weather data: {e}")
            
            # Use LangChain LLM for enhanced scheduling if available
            if self.llm_available and self.planting_schedule_prompt:
                try:
                    # Prepare context for LLM with real weather data
                    llm_context = await self._prepare_llm_context_for_planting_schedule(
                        recommendation, farmer_data, target_season, weather_data, weather_forecast
                    )
                    
                    # Generate LLM-enhanced schedule
                    llm_schedule = await self._generate_llm_planting_schedule(llm_context)
                    
                    if llm_schedule:
                        # Merge LLM insights with crop calendar data and weather
                        return await self._merge_llm_and_calendar_schedule(
                            llm_schedule, crop_calendar, target_season, weather_data
                        )
                        
                except Exception as e:
                    logger.warning(f"LLM planting schedule generation failed, falling back to rule-based: {e}")
            
            # Fallback to rule-based schedule generation with weather consideration
            if not crop_calendar:
                # Create default schedule
                current_date = datetime.now().date()
                planting_date = current_date + timedelta(days=30)
                
                # Adjust based on weather if available
                if weather_data:
                    if weather_data.temperature < 15:
                        planting_date += timedelta(days=7)  # Delay if too cold
                    elif weather_data.rainfall > 50:
                        planting_date += timedelta(days=3)  # Delay if heavy rain
                
                return PlantingSchedule(
                    optimal_planting_date=planting_date,
                    planting_window_start=planting_date - timedelta(days=15),
                    planting_window_end=planting_date + timedelta(days=15),
                    critical_factors=["Weather conditions", "Soil moisture"],
                    preparation_tasks=["Land preparation", "Seed procurement"],
                    weather_considerations=["Avoid heavy rainfall", "Ensure adequate soil moisture"]
                )
            
            # Use crop calendar data with weather adjustments
            optimal_date = crop_calendar.optimal_planting_start or datetime.now().date()
            
            # Adjust optimal date based on current weather
            if weather_data:
                if weather_data.temperature < 15:
                    optimal_date += timedelta(days=5)  # Delay if too cold
                elif weather_data.rainfall > 50:
                    optimal_date += timedelta(days=2)  # Delay if heavy rain
            
            window_start = crop_calendar.optimal_planting_start or (optimal_date - timedelta(days=15))
            window_end = crop_calendar.optimal_planting_end or (optimal_date + timedelta(days=15))
            
            # Add weather-specific considerations
            weather_considerations = ["Monitor weather forecast", "Ensure soil moisture"]
            if weather_data:
                if weather_data.temperature < 20:
                    weather_considerations.append("Monitor temperature for optimal planting conditions")
                if weather_data.humidity > 80:
                    weather_considerations.append("High humidity may affect soil preparation")
                if weather_data.rainfall > 30:
                    weather_considerations.append("Heavy rainfall may delay planting")
            
            return PlantingSchedule(
                optimal_planting_date=optimal_date,
                planting_window_start=window_start,
                planting_window_end=window_end,
                critical_factors=["Optimal planting window", "Crop-specific requirements", "Weather conditions"],
                preparation_tasks=["Land preparation", "Seed procurement", "Fertilizer application"],
                weather_considerations=weather_considerations
            )
            
        except Exception as e:
            logger.error(f"Error generating planting schedule: {e}")
            # Return safe default
            current_date = datetime.now().date()
            return PlantingSchedule(
                optimal_planting_date=current_date + timedelta(days=30),
                planting_window_start=current_date + timedelta(days=15),
                planting_window_end=current_date + timedelta(days=45),
                critical_factors=["Basic weather monitoring", "Soil preparation"],
                preparation_tasks=["Land preparation", "Seed procurement"],
                weather_considerations=["Avoid extreme weather", "Ensure soil moisture"]
            )
    
    async def _calculate_resource_requirements(
        self, 
        recommendation: CropRecommendation, 
        farmer_data: Any, 
        area_acres: float
    ) -> ResourceRequirement:
        """Calculate resource requirements for the crop plan"""
        try:
            # Get crop calendar for detailed requirements
            crop_calendar = next((cal for cal in farmer_data.crop_calendars 
                                if cal.crop_name.lower() == recommendation.crop_name.lower()), None)
            
            # Base requirements per acre
            base_requirements = {
                "rice": {
                    "seeds": 25.0,  # kg per acre
                    "fertilizers": {"N": 120.0, "P": 60.0, "K": 40.0},  # kg per acre
                    "pesticides": 2.0,  # liters per acre
                    "water": 1200.0,  # mm per acre
                    "labor": 25.0,  # days per acre
                    "equipment": 8.0  # hours per acre
                },
                "wheat": {
                    "seeds": 100.0,
                    "fertilizers": {"N": 100.0, "P": 50.0, "K": 30.0},
                    "pesticides": 1.5,
                    "water": 800.0,
                    "labor": 20.0,
                    "equipment": 6.0
                },
                "maize": {
                    "seeds": 20.0,
                    "fertilizers": {"N": 150.0, "P": 75.0, "K": 50.0},
                    "pesticides": 2.5,
                    "water": 600.0,
                    "labor": 18.0,
                    "equipment": 7.0
                }
            }
            
            # Get requirements for the crop
            crop_req = base_requirements.get(recommendation.crop_name.lower(), {
                "seeds": 50.0,
                "fertilizers": {"N": 100.0, "P": 50.0, "K": 30.0},
                "pesticides": 2.0,
                "water": 800.0,
                "labor": 20.0,
                "equipment": 6.0
            })
            
            # Calculate total requirements
            total_seeds = crop_req["seeds"] * area_acres
            total_fertilizers = {k: v * area_acres for k, v in crop_req["fertilizers"].items()}
            total_pesticides = crop_req["pesticides"] * area_acres
            total_water = crop_req["water"] * area_acres
            total_labor = crop_req["labor"] * area_acres
            total_equipment = crop_req["equipment"] * area_acres
            
            # Estimate costs (simplified)
            seed_cost = total_seeds * 50.0  # ₹50 per kg
            fertilizer_cost = sum(total_fertilizers.values()) * 20.0  # ₹20 per kg
            pesticide_cost = total_pesticides * 500.0  # ₹500 per liter
            labor_cost = total_labor * 300.0  # ₹300 per day
            equipment_cost = total_equipment * 200.0  # ₹200 per hour
            
            total_cost = seed_cost + fertilizer_cost + pesticide_cost + labor_cost + equipment_cost
            
            return ResourceRequirement(
                seeds_kg_per_acre=crop_req["seeds"],
                fertilizers_kg_per_acre=crop_req["fertilizers"],
                pesticides_liters_per_acre=crop_req["pesticides"],
                water_requirement_mm=crop_req["water"],
                labor_days_per_acre=crop_req["labor"],
                equipment_hours_per_acre=crop_req["equipment"],
                estimated_cost_per_acre=total_cost / area_acres
            )
            
        except Exception as e:
            logger.error(f"Error calculating resource requirements: {e}")
            raise
    
    async def _perform_financial_planning(
        self, 
        recommendation: CropRecommendation, 
        resource_requirements: ResourceRequirement, 
        farmer_data: Any
    ) -> Dict[str, float]:
        """Perform financial planning for the crop plan"""
        try:
            area_acres = 1.0  # Default to 1 acre for calculations
            
            # Calculate investment
            investment = resource_requirements.estimated_cost_per_acre * area_acres
            
            # Calculate expected revenue
            expected_yield = recommendation.expected_yield_per_acre * area_acres
            
            # Market prices per quintal (simplified)
            market_prices = {
                "rice": 2000.0,
                "wheat": 2200.0,
                "maize": 1800.0,
                "cotton": 6000.0,
                "sugarcane": 350.0
            }
            
            price_per_quintal = market_prices.get(recommendation.crop_name.lower(), 2000.0)
            revenue = expected_yield * price_per_quintal / 100.0  # Convert to quintals
            
            # Calculate subsidy benefits
            subsidy_benefits = 0.0
            for scheme_match in farmer_data.eligible_schemes:
                if scheme_match.scheme.category.value in ["fertilizer_subsidy", "seed_subsidy"]:
                    subsidy_benefits += scheme_match.estimated_benefit or 0.0
            
            # Calculate net profit
            net_profit = revenue - investment + subsidy_benefits
            
            return {
                "estimated_investment": investment,
                "expected_revenue": revenue,
                "subsidy_benefits": subsidy_benefits,
                "net_profit_estimate": net_profit
            }
            
        except Exception as e:
            logger.error(f"Error performing financial planning: {e}")
            return {
                "estimated_investment": 0.0,
                "expected_revenue": 0.0,
                "subsidy_benefits": 0.0,
                "net_profit_estimate": 0.0
            }
    
    async def _assess_risks_and_mitigation(
        self, 
        recommendation: CropRecommendation, 
        farmer_data: Any, 
        planting_schedule: PlantingSchedule
    ) -> Dict[str, List[str]]:
        """Assess risks and provide mitigation strategies using LangChain LLM"""
        try:
            # Use LangChain LLM for enhanced risk assessment if available
            if self.llm_available and self.risk_assessment_prompt:
                try:
                    # Prepare context for LLM
                    llm_context = await self._prepare_llm_context_for_risk_assessment(
                        recommendation, farmer_data, planting_schedule
                    )
                    
                    # Generate LLM-enhanced risk assessment
                    llm_assessment = await self._generate_llm_risk_assessment(llm_context)
                    
                    if llm_assessment:
                        # Merge LLM insights with rule-based assessment
                        return await self._merge_llm_and_rule_based_risk_assessment(
                            llm_assessment, recommendation, farmer_data, planting_schedule
                        )
                        
                except Exception as e:
                    logger.warning(f"LLM risk assessment failed, falling back to rule-based: {e}")
            
            # Fallback to rule-based risk assessment
            return await self._generate_rule_based_risk_assessment(
                recommendation, farmer_data, planting_schedule
            )
            
        except Exception as e:
            logger.error(f"Error assessing risks and mitigation: {e}")
            return {
                "risk_factors": ["Risk assessment incomplete"],
                "mitigation_strategies": ["Consult local agriculture experts"],
                "insurance_recommendations": ["Consider government crop insurance schemes"]
            }
    
    async def _prepare_llm_context_for_risk_assessment(
        self,
        recommendation: CropRecommendation,
        farmer_data: Any,
        planting_schedule: PlantingSchedule
    ) -> Dict[str, Any]:
        """Prepare context data for LLM risk assessment"""
        try:
            # Extract farmer profile data
            farmer_profile = getattr(farmer_data, 'farmer_profile', {})
            
            # Get location information
            location = "Unknown"
            if hasattr(farmer_data, 'farmer_profile') and farmer_data.farmer_profile:
                profile = farmer_data.farmer_profile
                if hasattr(profile, 'pincode') and profile.pincode:
                    location = f"Pincode: {profile.pincode}"
                elif hasattr(profile, 'lat') and hasattr(profile, 'lon') and profile.lat and profile.lon:
                    location = f"Coordinates: {profile.lat}, {profile.lon}"
            
            # Get weather forecast (placeholder - would integrate with weather service)
            weather_forecast = "Moderate temperatures, occasional rainfall expected"
            
            context = {
                "crop_name": recommendation.crop_name,
                "crop_variety": recommendation.crop_variety,
                "season": getattr(recommendation, 'season', 'Unknown'),
                "location": location,
                "farm_size": getattr(farmer_profile, 'farm_size', 'Unknown'),
                "experience_years": getattr(farmer_profile, 'experience_years', 'Unknown'),
                "soil_suitability_score": recommendation.soil_suitability_score,
                "climate_suitability_score": recommendation.climate_suitability_score,
                "market_demand_score": recommendation.market_demand_score,
                "weather_forecast": weather_forecast,
                "planting_date": planting_schedule.optimal_planting_date.isoformat() if planting_schedule.optimal_planting_date else "Unknown"
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error preparing LLM context for risk assessment: {e}")
            return {}
    
    async def _generate_llm_risk_assessment(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate risk assessment using LangChain LLM"""
        try:
            if not self.llm or not self.risk_assessment_prompt:
                return None
            
            # Format prompt with context
            formatted_prompt = self.risk_assessment_prompt.format(**context)
            
            # Generate response using LLM
            messages = [HumanMessage(content=formatted_prompt)]
            response = await self.llm.agenerate([messages])
            
            if response.generations and response.generations[0]:
                llm_response = response.generations[0][0].text
                
                # Try to parse JSON response
                try:
                    # Extract JSON from response (handle markdown formatting)
                    json_start = llm_response.find('{')
                    json_end = llm_response.rfind('}') + 1
                    
                    if json_start != -1 and json_end != 0:
                        json_str = llm_response[json_start:json_end]
                        parsed_response = json.loads(json_str)
                        logger.info(f"LLM risk assessment generated successfully for {context.get('crop_name', 'unknown')}")
                        return parsed_response
                    else:
                        logger.warning("No JSON found in LLM response")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM response as JSON: {e}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating LLM risk assessment: {e}")
            return None
    
    async def _merge_llm_and_rule_based_risk_assessment(
        self,
        llm_assessment: Dict[str, Any],
        recommendation: CropRecommendation,
        farmer_data: Any,
        planting_schedule: PlantingSchedule
    ) -> Dict[str, List[str]]:
        """Merge LLM insights with rule-based risk assessment"""
        try:
            # Extract LLM assessment data
            llm_risk_factors = llm_assessment.get('risk_factors', [])
            llm_mitigation_strategies = llm_assessment.get('mitigation_strategies', [])
            llm_insurance_recommendations = llm_assessment.get('insurance_recommendations', [])
            llm_monitoring_checklist = llm_assessment.get('monitoring_checklist', [])
            llm_early_warning_signs = llm_assessment.get('early_warning_signs', [])
            llm_contingency_plans = llm_assessment.get('contingency_plans', [])
            llm_expert_consultation = llm_assessment.get('expert_consultation', [])
            
            # Generate rule-based assessment as fallback
            rule_based_assessment = await self._generate_rule_based_risk_assessment(
                recommendation, farmer_data, planting_schedule
            )
            
            # Merge risk factors
            all_risk_factors = llm_risk_factors + rule_based_assessment.get('risk_factors', [])
            
            # Merge mitigation strategies
            all_mitigation_strategies = llm_mitigation_strategies + rule_based_assessment.get('mitigation_strategies', [])
            
            # Merge insurance recommendations
            all_insurance_recommendations = llm_insurance_recommendations + rule_based_assessment.get('insurance_recommendations', [])
            
            # Remove duplicates while preserving order
            def remove_duplicates_preserve_order(items):
                seen = set()
                unique_items = []
                for item in items:
                    if item not in seen:
                        seen.add(item)
                        unique_items.append(item)
                return unique_items
            
            risk_factors = remove_duplicates_preserve_order(all_risk_factors)[:8]  # Limit to top 8
            mitigation_strategies = remove_duplicates_preserve_order(all_mitigation_strategies)[:8]  # Limit to top 8
            insurance_recommendations = remove_duplicates_preserve_order(all_insurance_recommendations)[:5]  # Limit to top 5
            
            # Add LLM-specific insights if available
            additional_insights = {}
            if llm_monitoring_checklist:
                additional_insights['monitoring_checklist'] = llm_monitoring_checklist[:5]
            if llm_early_warning_signs:
                additional_insights['early_warning_signs'] = llm_early_warning_signs[:5]
            if llm_contingency_plans:
                additional_insights['contingency_plans'] = llm_contingency_plans[:5]
            if llm_expert_consultation:
                additional_insights['expert_consultation'] = llm_expert_consultation[:3]
            
            result = {
                "risk_factors": risk_factors,
                "mitigation_strategies": mitigation_strategies,
                "insurance_recommendations": insurance_recommendations
            }
            
            # Add additional insights
            result.update(additional_insights)
            
            return result
            
        except Exception as e:
            logger.error(f"Error merging LLM and rule-based risk assessment: {e}")
            # Fallback to rule-based assessment
            return await self._generate_rule_based_risk_assessment(
                recommendation, farmer_data, planting_schedule
            )
    
    async def _generate_rule_based_risk_assessment(
        self,
        recommendation: CropRecommendation,
        farmer_data: Any,
        planting_schedule: PlantingSchedule
    ) -> Dict[str, List[str]]:
        """Generate rule-based risk assessment as fallback"""
        try:
            risk_factors = []
            mitigation_strategies = []
            insurance_recommendations = []
            
            # Soil-related risks
            if recommendation.soil_suitability_score < 0.7:
                risk_factors.append("Suboptimal soil conditions")
                mitigation_strategies.append("Apply soil amendments before planting")
                mitigation_strategies.append("Consider soil testing and targeted fertilization")
            
            # Climate-related risks
            if recommendation.climate_suitability_score < 0.7:
                risk_factors.append("Climate timing risks")
                mitigation_strategies.append("Monitor weather forecasts closely")
                mitigation_strategies.append("Consider adjusting planting schedule")
            
            # Market risks
            if recommendation.market_demand_score < 0.7:
                risk_factors.append("Market demand uncertainty")
                mitigation_strategies.append("Diversify crop portfolio")
                mitigation_strategies.append("Explore contract farming opportunities")
            
            # Insurance recommendations
            if recommendation.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                insurance_recommendations.append("Consider PM Fasal Bima Yojana")
                insurance_recommendations.append("Evaluate private crop insurance options")
            
            # General mitigation strategies
            mitigation_strategies.append("Implement integrated pest management")
            mitigation_strategies.append("Use drought-resistant varieties if available")
            mitigation_strategies.append("Maintain proper irrigation scheduling")
            
            return {
                "risk_factors": risk_factors,
                "mitigation_strategies": mitigation_strategies,
                "insurance_recommendations": insurance_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating rule-based risk assessment: {e}")
            return {
                "risk_factors": ["Risk assessment incomplete"],
                "mitigation_strategies": ["Consult local agriculture experts"],
                "insurance_recommendations": ["Consider government crop insurance schemes"]
            }
    
    async def _get_available_crops_for_season(self, farmer_data: Any, season: Season) -> List[str]:
        """Get available crops for a specific season"""
        try:
            available_crops = []
            
            # Get crops from crop calendars
            for calendar in farmer_data.crop_calendars:
                if calendar.season == season:
                    available_crops.append(calendar.crop_name)
            
            # Add common crops if no specific calendars
            if not available_crops:
                common_crops = {
                    Season.KHARIF: ["rice", "maize", "cotton", "sugarcane", "pulses"],
                    Season.RABI: ["wheat", "barley", "mustard", "chickpea", "lentil"],
                    Season.ZAID: ["vegetables", "fruits", "pulses"],
                    Season.SUMMER: ["vegetables", "fruits", "pulses"]
                }
                available_crops = common_crops.get(season, ["rice", "wheat"])
            
            return available_crops
            
        except Exception as e:
            logger.error(f"Error getting available crops: {e}")
            return ["rice", "wheat"]
    
    def _cache_plan(self, plan_id: str, plan: CropPlan):
        """Cache a crop plan"""
        try:
            self.plan_cache[plan_id] = plan
            
            # Limit cache size
            if len(self.plan_cache) > 100:
                # Remove oldest entries
                oldest_id = min(self.plan_cache.keys())
                del self.plan_cache[oldest_id]
                
        except Exception as e:
            logger.error(f"Error caching plan: {e}")
    
    async def get_cached_plan(self, plan_id: str) -> Optional[CropPlan]:
        """Get a cached crop plan"""
        try:
            return self.plan_cache.get(plan_id)
        except Exception as e:
            logger.error(f"Error getting cached plan: {e}")
            return None
    
    def export_plan_to_json(self, plan: CropPlan, filename: str) -> bool:
        """Export crop plan to JSON file"""
        try:
            # Convert plan to JSON-serializable format
            plan_data = {
                "plan_id": plan.plan_id,
                "farmer_id": plan.farmer_id,
                "crop_name": plan.crop_name,
                "crop_variety": plan.crop_variety,
                "season": plan.season.value,
                "area_acres": plan.area_acres,
                "status": plan.status.value,
                "recommendation": {
                    "confidence_score": plan.recommendation.confidence_score,
                    "reasoning": plan.recommendation.reasoning,
                    "expected_yield_per_acre": plan.recommendation.expected_yield_per_acre,
                    "risk_level": plan.recommendation.risk_level.value
                },
                "planting_schedule": {
                    "optimal_planting_date": plan.planting_schedule.optimal_planting_date.isoformat(),
                    "planting_window_start": plan.planting_schedule.planting_window_start.isoformat(),
                    "planting_window_end": plan.planting_schedule.planting_window_end.isoformat(),
                    "critical_factors": plan.planting_schedule.critical_factors,
                    "preparation_tasks": plan.planting_schedule.preparation_tasks
                },
                "resource_requirements": {
                    "estimated_cost_per_acre": plan.resource_requirements.estimated_cost_per_acre,
                    "seeds_kg_per_acre": plan.resource_requirements.seeds_kg_per_acre,
                    "water_requirement_mm": plan.resource_requirements.water_requirement_mm
                },
                "financial_planning": {
                    "estimated_investment": plan.estimated_investment,
                    "expected_revenue": plan.expected_revenue,
                    "subsidy_benefits": plan.subsidy_benefits,
                    "net_profit_estimate": plan.net_profit_estimate
                },
                "risk_assessment": {
                    "risk_factors": plan.risk_factors,
                    "mitigation_strategies": plan.mitigation_strategies,
                    "insurance_recommendations": plan.insurance_recommendations
                },
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat()
            }
            
            # Write to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported crop plan to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting crop plan: {e}")
            return False

    async def _prepare_llm_context_for_crop_analysis(
        self,
        crop_name: str,
        farmer_data: Any,
        season: Season,
        soil_suitability: float,
        climate_suitability: float,
        market_demand: float
    ) -> Dict[str, Any]:
        """Prepare context data for LLM crop analysis"""
        try:
            # Extract farmer profile data
            farmer_profile = getattr(farmer_data, 'farmer_profile', {})
            soil_health = getattr(farmer_data, 'soil_health', {})
            
            # Get location information
            location = "Unknown"
            if hasattr(farmer_data, 'farmer_profile') and farmer_data.farmer_profile:
                profile = farmer_data.farmer_profile
                if hasattr(profile, 'pincode') and profile.pincode:
                    location = f"Pincode: {profile.pincode}"
                elif hasattr(profile, 'lat') and hasattr(profile, 'lon') and profile.lat and profile.lon:
                    location = f"Coordinates: {profile.lat}, {profile.lon}"
            
            # Prepare soil health summary
            soil_summary = "No soil data available"
            if soil_health:
                ph_level = getattr(soil_health, 'ph_level', 'Unknown')
                organic_carbon = getattr(soil_health, 'organic_carbon', 'Unknown')
                nitrogen_n = getattr(soil_health, 'nitrogen_n', 'Unknown')
                phosphorus_p = getattr(soil_health, 'phosphorus_p', 'Unknown')
                potassium_k = getattr(soil_health, 'potassium_k', 'Unknown')
                
                soil_summary = f"pH: {ph_level}, OC: {organic_carbon}%, N: {nitrogen_n} kg/ha, P: {phosphorus_p} kg/ha, K: {potassium_k} kg/ha"
            
            context = {
                "crop_name": crop_name,
                "location": location,
                "farm_size": getattr(farmer_profile, 'farm_size', 'Unknown'),
                "experience_years": getattr(farmer_profile, 'experience_years', 'Unknown'),
                "irrigation_type": getattr(farmer_profile, 'irrigation_type', 'Unknown'),
                "soil_type": getattr(farmer_profile, 'soil_type', 'Unknown'),
                "language": getattr(farmer_profile, 'language', 'en'),
                "ph_level": getattr(soil_health, 'ph_level', 'Unknown'),
                "organic_carbon": getattr(soil_health, 'organic_carbon', 'Unknown'),
                "nitrogen_n": getattr(soil_health, 'nitrogen_n', 'Unknown'),
                "phosphorus_p": getattr(soil_health, 'phosphorus_p', 'Unknown'),
                "potassium_k": getattr(soil_health, 'potassium_k', 'Unknown'),
                "season": season.value,
                "available_crops": [crop.name for crop in getattr(farmer_data, 'crop_calendars', [])],
                "soil_suitability_score": soil_suitability,
                "climate_suitability_score": climate_suitability,
                "market_demand_score": market_demand
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error preparing LLM context: {e}")
            return {}
    
    async def _generate_llm_crop_recommendation(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate crop recommendation using LangChain LLM"""
        try:
            if not self.llm or not self.crop_recommendation_prompt:
                return None
            
            # Format prompt with context
            formatted_prompt = self.crop_recommendation_prompt.format(**context)
            
            # Generate response using LLM
            messages = [HumanMessage(content=formatted_prompt)]
            response = await self.llm.agenerate([messages])
            
            if response.generations and response.generations[0]:
                llm_response = response.generations[0][0].text
                
                # Try to parse JSON response
                try:
                    # Extract JSON from response (handle markdown formatting)
                    json_start = llm_response.find('{')
                    json_end = llm_response.rfind('}') + 1
                    
                    if json_start != -1 and json_end != 0:
                        json_str = llm_response[json_start:json_end]
                        parsed_response = json.loads(json_str)
                        logger.info(f"LLM crop recommendation generated successfully for {context.get('crop_name', 'unknown')}")
                        return parsed_response
                    else:
                        logger.warning("No JSON found in LLM response")
                        return None
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse LLM response as JSON: {e}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating LLM crop recommendation: {e}")
            return None
    
    async def _merge_llm_and_calculated_recommendation(
        self,
        llm_recommendation: Dict[str, Any],
        crop_name: str,
        crop_calendar: Any,
        soil_suitability: float,
        climate_suitability: float,
        market_demand: float
    ) -> CropRecommendation:
        """Merge LLM insights with calculated scores for comprehensive recommendation"""
        try:
            # Extract LLM insights
            llm_crop_name = llm_recommendation.get('crop_name', crop_name)
            llm_crop_variety = llm_recommendation.get('crop_variety', 'Standard')
            llm_confidence_score = llm_recommendation.get('confidence_score', 0.7)
            llm_reasoning = llm_recommendation.get('reasoning', [])
            llm_expected_yield = llm_recommendation.get('expected_yield_per_acre', 20.0)
            llm_market_demand = llm_recommendation.get('market_demand_score', market_demand)
            llm_risk_level = llm_recommendation.get('risk_level', 'medium')
            llm_soil_suitability = llm_recommendation.get('soil_suitability_score', soil_suitability)
            llm_climate_suitability = llm_recommendation.get('climate_suitability_score', climate_suitability)
            llm_financial_viability = llm_recommendation.get('financial_viability_score', 0.7)
            
            # Merge with calculated scores (weighted average)
            final_confidence_score = (llm_confidence_score * 0.7) + (self._calculate_confidence_score(soil_suitability, climate_suitability, market_demand) * 0.3)
            final_soil_suitability = (llm_soil_suitability * 0.6) + (soil_suitability * 0.4)
            final_climate_suitability = (llm_climate_suitability * 0.6) + (climate_suitability * 0.4)
            final_market_demand = (llm_market_demand * 0.7) + (market_demand * 0.3)
            
            # Convert risk level string to enum
            risk_level_enum = self._convert_risk_level_string(llm_risk_level)
            
            # Combine reasoning
            combined_reasoning = llm_reasoning + self._generate_reasoning(
                crop_name, soil_suitability, climate_suitability, market_demand
            )
            
            # Remove duplicates while preserving order
            seen = set()
            unique_reasoning = []
            for reason in combined_reasoning:
                if reason not in seen:
                    seen.add(reason)
                    unique_reasoning.append(reason)
            
            return CropRecommendation(
                crop_name=llm_crop_name,
                crop_variety=llm_crop_variety,
                confidence_score=final_confidence_score,
                reasoning=unique_reasoning[:5],  # Limit to top 5 reasons
                expected_yield_per_acre=llm_expected_yield,
                market_demand_score=final_market_demand,
                risk_level=risk_level_enum,
                soil_suitability_score=final_soil_suitability,
                climate_suitability_score=final_climate_suitability,
                financial_viability_score=llm_financial_viability
            )
            
        except Exception as e:
            logger.error(f"Error merging LLM and calculated recommendation: {e}")
            # Fallback to calculated recommendation
            return self._create_fallback_recommendation(
                crop_name, crop_calendar, soil_suitability, climate_suitability, market_demand
            )
    
    def _convert_risk_level_string(self, risk_level_str: str) -> RiskLevel:
        """Convert risk level string to RiskLevel enum"""
        try:
            risk_mapping = {
                "low": RiskLevel.LOW,
                "medium": RiskLevel.MEDIUM,
                "high": RiskLevel.HIGH,
                "critical": RiskLevel.CRITICAL
            }
            return risk_mapping.get(risk_level_str.lower(), RiskLevel.MEDIUM)
        except Exception:
            return RiskLevel.MEDIUM
    
    def _create_fallback_recommendation(
        self,
        crop_name: str,
        crop_calendar: Any,
        soil_suitability: float,
        climate_suitability: float,
        market_demand: float
    ) -> CropRecommendation:
        """Create fallback recommendation when LLM fails"""
        confidence_score = self._calculate_confidence_score(
            soil_suitability, climate_suitability, market_demand
        )
        risk_level = self._assess_risk_level(soil_suitability, climate_suitability)
        reasoning = self._generate_reasoning(
            crop_name, soil_suitability, climate_suitability, market_demand
        )
        
        return CropRecommendation(
            crop_name=crop_name,
            crop_variety=crop_calendar.crop_variety if crop_calendar else "Standard",
            confidence_score=confidence_score,
            reasoning=reasoning,
            expected_yield_per_acre=self._estimate_yield(crop_name, soil_suitability),
            market_demand_score=market_demand,
            risk_level=risk_level,
            soil_suitability_score=soil_suitability,
            climate_suitability_score=climate_suitability,
            financial_viability_score=self._calculate_financial_viability(
                crop_name, market_demand, risk_level
            )
        )

# Example usage and testing
async def test_crop_planning_engine():
    """Test the crop planning engine"""
    engine = CropPlanningEngine()
    
    # Test farmer profile
    farmer_profile = {
        "client_id": "test_farmer_002",
        "pincode": "560001",
        "lat": 12.9716,
        "lon": 77.5946,
        "district": "Bangalore",
        "state": "Karnataka",
        "farm_size": 3.0,
        "crop_preferences": ["rice", "wheat", "maize"]
    }
    
    try:
        # Generate crop plan
        print("Generating crop plan...")
        crop_plan = await engine.generate_crop_plan(farmer_profile)
        
        print(f"\n✅ Crop plan generated successfully!")
        print(f"Plan ID: {crop_plan.plan_id}")
        print(f"Crop: {crop_plan.crop_name} ({crop_plan.crop_variety})")
        print(f"Season: {crop_plan.season.value}")
        print(f"Area: {crop_plan.area_acres} acres")
        print(f"Status: {crop_plan.status.value}")
        
        print(f"\nRecommendation:")
        print(f"  Confidence Score: {crop_plan.recommendation.confidence_score:.2f}")
        print(f"  Expected Yield: {crop_plan.recommendation.expected_yield_per_acre:.1f} quintals/acre")
        print(f"  Risk Level: {crop_plan.recommendation.risk_level.value}")
        print(f"  Reasoning: {', '.join(crop_plan.recommendation.reasoning)}")
        
        print(f"\nPlanting Schedule:")
        print(f"  Optimal Date: {crop_plan.planting_schedule.optimal_planting_date}")
        print(f"  Window: {crop_plan.planting_schedule.planting_window_start} to {crop_plan.planting_schedule.planting_window_end}")
        print(f"  Critical Factors: {', '.join(crop_plan.planting_schedule.critical_factors)}")
        
        print(f"\nFinancial Planning:")
        print(f"  Investment: ₹{crop_plan.estimated_investment:,.0f}")
        print(f"  Expected Revenue: ₹{crop_plan.expected_revenue:,.0f}")
        print(f"  Subsidy Benefits: ₹{crop_plan.subsidy_benefits:,.0f}")
        print(f"  Net Profit: ₹{crop_plan.net_profit_estimate:,.0f}")
        
        print(f"\nRisk Assessment:")
        print(f"  Risk Factors: {', '.join(crop_plan.risk_factors)}")
        print(f"  Mitigation: {', '.join(crop_plan.mitigation_strategies[:2])}")
        
        # Export plan
        export_success = engine.export_plan_to_json(crop_plan, "test_crop_plan.json")
        print(f"\nPlan Export: {'✅ Success' if export_success else '❌ Failed'}")
        
    except Exception as e:
        print(f"❌ Error testing crop planning engine: {e}")
        logger.error(f"Error testing crop planning engine: {e}")

if __name__ == "__main__":
    asyncio.run(test_crop_planning_engine())
