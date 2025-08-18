"""
Risk Assessment & Alert Service
Monitors weather, pests, market conditions and provides proactive alerts
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
from app.services.weather_tool import WeatherTool
from app.services.market_tool import MarketTool
from app.services.crop_calendar_service import CropCalendar
from app.config import settings

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"
    CRITICAL = "critical"

class RiskCategory(Enum):
    """Risk categories"""
    WEATHER = "weather"
    PEST_DISEASE = "pest_disease"
    MARKET = "market"
    SOIL = "soil"
    IRRIGATION = "irrigation"
    FINANCIAL = "financial"

@dataclass
class RiskFactor:
    """Individual risk factor"""
    risk_id: str
    category: RiskCategory
    severity: AlertSeverity
    title: str
    description: str
    impact_score: float  # 0.0 to 1.0
    probability: float  # 0.0 to 1.0
    risk_score: float  # impact * probability
    affected_crops: List[str]
    affected_regions: List[str]
    mitigation_strategies: List[str]
    detection_date: datetime
    expiry_date: Optional[datetime] = None
    is_active: bool = True

@dataclass
class Alert:
    """Alert notification"""
    alert_id: str
    risk_factor: RiskFactor
    farmer_id: str
    crop_name: str
    alert_type: str  # "immediate", "daily", "weekly"
    message: str
    severity: AlertSeverity
    created_at: datetime
    read_at: Optional[datetime] = None
    action_taken: Optional[str] = None
    is_dismissed: bool = False

@dataclass
class RiskAssessment:
    """Complete risk assessment for a farmer/crop"""
    assessment_id: str
    farmer_id: str
    crop_name: str
    assessment_date: datetime
    
    # Risk factors
    active_risks: List[RiskFactor]
    risk_score: float  # Overall risk score
    
    # Weather risks
    weather_risks: List[RiskFactor]
    weather_risk_score: float
    
    # Pest and disease risks
    pest_risks: List[RiskFactor]
    pest_risk_score: float
    
    # Market risks
    market_risks: List[RiskFactor]
    market_risk_score: float
    
    # Recommendations
    immediate_actions: List[str]
    preventive_measures: List[str]
    insurance_recommendations: List[str]

class RiskAssessmentService:
    """Service for assessing agricultural risks and generating alerts"""
    
    def __init__(self):
        self.weather_tool = WeatherTool()
        self.market_tool = MarketTool()
        self.risk_cache = {}
        self.alert_cache = {}
        
        # Risk thresholds
        self.high_risk_threshold = 0.7
        self.medium_risk_threshold = 0.4
        self.low_risk_threshold = 0.2
        
        # Initialize risk patterns
        self.risk_patterns = self._initialize_risk_patterns()
        
    def _initialize_risk_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk patterns for different scenarios"""
        patterns = {
            "drought": {
                "triggers": ["low_rainfall", "high_temperature", "low_soil_moisture"],
                "affected_stages": ["germination", "vegetative", "flowering"],
                "mitigation": ["irrigation_scheduling", "drought_resistant_varieties", "mulching"],
                "impact_score": 0.8
            },
            "flooding": {
                "triggers": ["heavy_rainfall", "high_water_level", "poor_drainage"],
                "affected_stages": ["all"],
                "mitigation": ["drainage_improvement", "raised_beds", "early_harvest"],
                "impact_score": 0.9
            },
            "pest_outbreak": {
                "triggers": ["high_humidity", "warm_temperature", "crop_stress"],
                "affected_stages": ["vegetative", "flowering", "fruiting"],
                "mitigation": ["pest_monitoring", "biological_control", "chemical_treatment"],
                "impact_score": 0.7
            },
            "market_volatility": {
                "triggers": ["supply_demand_imbalance", "export_restrictions", "weather_events"],
                "affected_stages": ["maturity", "harvest"],
                "mitigation": ["contract_farming", "storage_facilities", "diversification"],
                "impact_score": 0.6
            }
        }
        return patterns
    
    async def assess_farmer_risks(
        self,
        farmer_id: str,
        crop_name: str,
        location: Dict[str, float],  # lat, lng
        current_stage: str,
        force_refresh: bool = False
    ) -> RiskAssessment:
        """
        Assess risks for a specific farmer and crop
        
        Args:
            farmer_id: Farmer's ID
            crop_name: Name of the crop
            location: Farmer's location coordinates
            current_stage: Current growth stage
            force_refresh: Force refresh of risk data
            
        Returns:
            RiskAssessment object
        """
        try:
            logger.info(f"Assessing risks for farmer {farmer_id}, crop {crop_name}")
            
            # Check cache first
            cache_key = f"{farmer_id}_{crop_name}_{datetime.now().strftime('%Y%m%d')}"
            if not force_refresh and cache_key in self.risk_cache:
                return self.risk_cache[cache_key]
            
            # Assess different risk categories
            weather_risks = await self._assess_weather_risks(location, crop_name, current_stage)
            pest_risks = await self._assess_pest_risks(location, crop_name, current_stage)
            market_risks = await self._assess_market_risks(crop_name, location)
            
            # Combine all risks
            all_risks = weather_risks + pest_risks + market_risks
            active_risks = [risk for risk in all_risks if risk.is_active]
            
            # Calculate risk scores
            overall_risk_score = self._calculate_overall_risk_score(active_risks)
            weather_risk_score = self._calculate_category_risk_score(weather_risks)
            pest_risk_score = self._calculate_category_risk_score(pest_risks)
            market_risk_score = self._calculate_category_risk_score(market_risks)
            
            # Generate recommendations
            immediate_actions = self._generate_immediate_actions(active_risks)
            preventive_measures = self._generate_preventive_measures(active_risks)
            insurance_recommendations = self._generate_insurance_recommendations(overall_risk_score)
            
            # Create assessment
            assessment = RiskAssessment(
                assessment_id=f"risk_{farmer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                farmer_id=farmer_id,
                crop_name=crop_name,
                assessment_date=datetime.now(),
                active_risks=active_risks,
                risk_score=overall_risk_score,
                weather_risks=weather_risks,
                weather_risk_score=weather_risk_score,
                pest_risks=pest_risks,
                pest_risk_score=pest_risk_score,
                market_risks=market_risks,
                market_risk_score=market_risk_score,
                immediate_actions=immediate_actions,
                preventive_measures=preventive_measures,
                insurance_recommendations=insurance_recommendations
            )
            
            # Cache assessment
            self._cache_assessment(cache_key, assessment)
            
            logger.info(f"Risk assessment completed for {farmer_id}: Overall score {overall_risk_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing farmer risks: {e}")
            raise
    
    async def _assess_weather_risks(
        self, 
        location: Dict[str, float], 
        crop_name: str, 
        current_stage: str
    ) -> List[RiskFactor]:
        """Assess weather-related risks"""
        try:
            weather_risks = []
            
            # Get current weather data
            weather_data = await self.weather_tool.get_current_weather(
                lat=location["lat"], 
                lon=location["lng"]
            )
            
            if not weather_data:
                return weather_risks
            
            # Check for drought conditions
            if weather_data.get("rainfall", 0) < 5.0 and weather_data.get("temperature", 0) > 30:
                drought_risk = RiskFactor(
                    risk_id=f"drought_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.WEATHER,
                    severity=AlertSeverity.ALERT,
                    title="Drought Risk Detected",
                    description="Low rainfall and high temperature indicate drought conditions",
                    impact_score=0.8,
                    probability=0.7,
                    risk_score=0.56,
                    affected_crops=[crop_name],
                    affected_regions=["current_location"],
                    mitigation_strategies=[
                        "Implement irrigation scheduling",
                        "Use drought-resistant varieties",
                        "Apply mulch to retain soil moisture"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=7)
                )
                weather_risks.append(drought_risk)
            
            # Check for flooding risk
            if weather_data.get("rainfall", 0) > 50.0:
                flood_risk = RiskFactor(
                    risk_id=f"flood_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.WEATHER,
                    severity=AlertSeverity.CRITICAL,
                    title="Flooding Risk Detected",
                    description="Heavy rainfall may cause flooding and waterlogging",
                    impact_score=0.9,
                    probability=0.6,
                    risk_score=0.54,
                    affected_crops=[crop_name],
                    affected_regions=["current_location"],
                    mitigation_strategies=[
                        "Improve drainage systems",
                        "Use raised beds",
                        "Monitor water levels closely"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=3)
                )
                weather_risks.append(flood_risk)
            
            # Check for temperature stress
            if weather_data.get("temperature", 0) > 35:
                temp_risk = RiskFactor(
                    risk_id=f"temp_stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.WEATHER,
                    severity=AlertSeverity.WARNING,
                    title="Temperature Stress Risk",
                    description="High temperature may cause heat stress in crops",
                    impact_score=0.6,
                    probability=0.8,
                    risk_score=0.48,
                    affected_crops=[crop_name],
                    affected_regions=["current_location"],
                    mitigation_strategies=[
                        "Increase irrigation frequency",
                        "Provide shade if possible",
                        "Monitor for heat stress symptoms"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=5)
                )
                weather_risks.append(temp_risk)
            
            return weather_risks
            
        except Exception as e:
            logger.error(f"Error assessing weather risks: {e}")
            return []
    
    async def _assess_pest_risks(
        self, 
        location: Dict[str, float], 
        crop_name: str, 
        current_stage: str
    ) -> List[RiskFactor]:
        """Assess pest and disease risks"""
        try:
            pest_risks = []
            
            # Get weather data for pest risk assessment
            weather_data = await self.weather_tool.get_current_weather(
                lat=location["lat"], 
                lon=location["lng"]
            )
            
            if not weather_data:
                return pest_risks
            
            # Check for conditions favorable to pests
            humidity = weather_data.get("humidity", 50)
            temperature = weather_data.get("temperature", 25)
            
            # High humidity and warm temperature favor pest development
            if humidity > 70 and temperature > 25:
                pest_risk = RiskFactor(
                    risk_id=f"pest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.PEST_DISEASE,
                    severity=AlertSeverity.WARNING,
                    title="Pest Development Risk",
                    description="High humidity and warm temperature favor pest development",
                    impact_score=0.7,
                    probability=0.6,
                    risk_score=0.42,
                    affected_crops=[crop_name],
                    affected_regions=["current_location"],
                    mitigation_strategies=[
                        "Monitor for pest activity",
                        "Implement integrated pest management",
                        "Consider preventive treatments"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=10)
                )
                pest_risks.append(pest_risk)
            
            # Stage-specific pest risks
            if current_stage in ["flowering", "fruiting"]:
                stage_pest_risk = RiskFactor(
                    risk_id=f"stage_pest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.PEST_DISEASE,
                    severity=AlertSeverity.ALERT,
                    title="Critical Stage Pest Risk",
                    description=f"Crop is in {current_stage} stage, vulnerable to pests",
                    impact_score=0.8,
                    probability=0.5,
                    risk_score=0.40,
                    affected_crops=[crop_name],
                    affected_regions=["current_location"],
                    mitigation_strategies=[
                        "Increase monitoring frequency",
                        "Protect flowers/fruits",
                        "Use appropriate pest control methods"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=14)
                )
                pest_risks.append(stage_pest_risk)
            
            return pest_risks
            
        except Exception as e:
            logger.error(f"Error assessing pest risks: {e}")
            return []
    
    async def _assess_market_risks(
        self, 
        crop_name: str, 
        location: Dict[str, float]
    ) -> List[RiskFactor]:
        """Assess market-related risks"""
        try:
            market_risks = []
            
            # Get market data
            market_data = await self.market_tool.get_current_prices(crop_name)
            
            if not market_data:
                return market_risks
            
            # Check for price volatility
            if market_data.get("price_change_percent", 0) > 10:
                volatility_risk = RiskFactor(
                    risk_id=f"volatility_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.MARKET,
                    severity=AlertSeverity.WARNING,
                    title="Market Price Volatility",
                    description="Significant price change detected in market",
                    impact_score=0.6,
                    probability=0.7,
                    risk_score=0.42,
                    affected_crops=[crop_name],
                    affected_regions=["all"],
                    mitigation_strategies=[
                        "Monitor market trends closely",
                        "Consider contract farming",
                        "Plan harvest timing strategically"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=30)
                )
                market_risks.append(volatility_risk)
            
            # Check for supply-demand imbalance
            if market_data.get("supply_status") == "low":
                supply_risk = RiskFactor(
                    risk_id=f"supply_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=RiskCategory.MARKET,
                    severity=AlertSeverity.INFO,
                    title="Low Supply Alert",
                    description="Market supply is currently low",
                    impact_score=0.5,
                    probability=0.8,
                    risk_score=0.40,
                    affected_crops=[crop_name],
                    affected_regions=["all"],
                    mitigation_strategies=[
                        "Plan for potential price increase",
                        "Consider storage options",
                        "Monitor supply trends"
                    ],
                    detection_date=datetime.now(),
                    expiry_date=datetime.now() + timedelta(days=14)
                )
                market_risks.append(supply_risk)
            
            return market_risks
            
        except Exception as e:
            logger.error(f"Error assessing market risks: {e}")
            return []
    
    def _calculate_overall_risk_score(self, risks: List[RiskFactor]) -> float:
        """Calculate overall risk score"""
        try:
            if not risks:
                return 0.0
            
            # Weighted average based on severity
            severity_weights = {
                AlertSeverity.INFO: 0.2,
                AlertSeverity.WARNING: 0.4,
                AlertSeverity.ALERT: 0.6,
                AlertSeverity.CRITICAL: 0.8
            }
            
            weighted_scores = []
            for risk in risks:
                weight = severity_weights.get(risk.severity, 0.5)
                weighted_score = risk.risk_score * weight
                weighted_scores.append(weighted_score)
            
            overall_score = sum(weighted_scores) / len(weighted_scores)
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            return 0.0
    
    def _calculate_category_risk_score(self, risks: List[RiskFactor]) -> float:
        """Calculate risk score for a specific category"""
        try:
            if not risks:
                return 0.0
            
            # Simple average of risk scores
            risk_scores = [risk.risk_score for risk in risks]
            category_score = sum(risk_scores) / len(risk_scores)
            
            return min(1.0, max(0.0, category_score))
            
        except Exception as e:
            logger.error(f"Error calculating category risk score: {e}")
            return 0.0
    
    def _generate_immediate_actions(self, risks: List[RiskFactor]) -> List[str]:
        """Generate immediate action recommendations"""
        try:
            actions = []
            
            # Sort risks by severity and impact
            sorted_risks = sorted(risks, key=lambda x: (x.severity.value, x.impact_score), reverse=True)
            
            for risk in sorted_risks[:3]:  # Top 3 most critical risks
                if risk.severity in [AlertSeverity.CRITICAL, AlertSeverity.ALERT]:
                    actions.extend(risk.mitigation_strategies[:2])  # Top 2 strategies
            
            # Remove duplicates
            unique_actions = list(set(actions))
            
            return unique_actions[:5]  # Limit to 5 actions
            
        except Exception as e:
            logger.error(f"Error generating immediate actions: {e}")
            return ["Monitor crop conditions closely", "Check weather forecast"]
    
    def _generate_preventive_measures(self, risks: List[RiskFactor]) -> List[str]:
        """Generate preventive measure recommendations"""
        try:
            measures = []
            
            # General preventive measures
            general_measures = [
                "Implement regular monitoring schedule",
                "Maintain proper irrigation systems",
                "Use integrated pest management",
                "Keep records of all activities",
                "Have contingency plans ready"
            ]
            
            measures.extend(general_measures)
            
            # Risk-specific preventive measures
            for risk in risks:
                if risk.severity in [AlertSeverity.WARNING, AlertSeverity.INFO]:
                    measures.extend(risk.mitigation_strategies[:1])
            
            # Remove duplicates and limit
            unique_measures = list(set(measures))
            return unique_measures[:8]
            
        except Exception as e:
            logger.error(f"Error generating preventive measures: {e}")
            return ["Implement regular monitoring", "Maintain proper irrigation"]
    
    def _generate_insurance_recommendations(self, overall_risk_score: float) -> List[str]:
        """Generate insurance recommendations based on risk score"""
        try:
            recommendations = []
            
            if overall_risk_score >= self.high_risk_threshold:
                recommendations.extend([
                    "Consider PM Fasal Bima Yojana (PMFBY)",
                    "Evaluate private crop insurance options",
                    "Look into weather-based insurance products"
                ])
            elif overall_risk_score >= self.medium_risk_threshold:
                recommendations.extend([
                    "Consider PM Fasal Bima Yojana (PMFBY)",
                    "Evaluate insurance needs based on crop value"
                ])
            else:
                recommendations.append("Standard PMFBY coverage may be sufficient")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating insurance recommendations: {e}")
            return ["Consider government crop insurance schemes"]
    
    async def generate_alerts(
        self, 
        risk_assessment: RiskAssessment,
        alert_type: str = "immediate"
    ) -> List[Alert]:
        """Generate alerts based on risk assessment"""
        try:
            alerts = []
            
            # Filter risks based on alert type
            if alert_type == "immediate":
                target_risks = [r for r in risk_assessment.active_risks 
                              if r.severity in [AlertSeverity.CRITICAL, AlertSeverity.ALERT]]
            elif alert_type == "daily":
                target_risks = [r for r in risk_assessment.active_risks 
                              if r.severity in [AlertSeverity.WARNING, AlertSeverity.INFO]]
            else:
                target_risks = risk_assessment.active_risks
            
            # Generate alerts for each risk
            for risk in target_risks:
                alert = Alert(
                    alert_id=f"alert_{risk.risk_id}_{datetime.now().strftime('%H%M%S')}",
                    risk_factor=risk,
                    farmer_id=risk_assessment.farmer_id,
                    crop_name=risk_assessment.crop_name,
                    alert_type=alert_type,
                    message=f"{risk.title}: {risk.description}",
                    severity=risk.severity,
                    created_at=datetime.now()
                )
                alerts.append(alert)
            
            # Cache alerts
            for alert in alerts:
                self._cache_alert(alert.alert_id, alert)
            
            logger.info(f"Generated {len(alerts)} {alert_type} alerts for {risk_assessment.farmer_id}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return []
    
    def _cache_assessment(self, cache_key: str, assessment: RiskAssessment):
        """Cache a risk assessment"""
        try:
            self.risk_cache[cache_key] = assessment
            
            # Limit cache size
            if len(self.risk_cache) > 50:
                # Remove oldest entries
                oldest_key = min(self.risk_cache.keys())
                del self.risk_cache[oldest_key]
                
        except Exception as e:
            logger.error(f"Error caching assessment: {e}")
    
    def _cache_alert(self, alert_id: str, alert: Alert):
        """Cache an alert"""
        try:
            self.alert_cache[alert_id] = alert
            
            # Limit cache size
            if len(self.alert_cache) > 100:
                # Remove oldest entries
                oldest_id = min(self.alert_cache.keys())
                del self.alert_cache[oldest_id]
                
        except Exception as e:
            logger.error(f"Error caching alert: {e}")
    
    def export_assessment_to_json(self, assessment: RiskAssessment, filename: str) -> bool:
        """Export risk assessment to JSON file"""
        try:
            # Convert assessment to JSON-serializable format
            assessment_data = {
                "assessment_id": assessment.assessment_id,
                "farmer_id": assessment.farmer_id,
                "crop_name": assessment.crop_name,
                "assessment_date": assessment.assessment_date.isoformat(),
                "overall_risk_score": assessment.risk_score,
                "weather_risk_score": assessment.weather_risk_score,
                "pest_risk_score": assessment.pest_risk_score,
                "market_risk_score": assessment.market_risk_score,
                "active_risks": [
                    {
                        "category": risk.category.value,
                        "severity": risk.severity.value,
                        "title": risk.title,
                        "description": risk.description,
                        "risk_score": risk.risk_score,
                        "mitigation_strategies": risk.mitigation_strategies
                    } for risk in assessment.active_risks
                ],
                "immediate_actions": assessment.immediate_actions,
                "preventive_measures": assessment.preventive_measures,
                "insurance_recommendations": assessment.insurance_recommendations
            }
            
            # Write to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(assessment_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported risk assessment to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting risk assessment: {e}")
            return False

# Example usage and testing
async def test_risk_assessment_service():
    """Test the risk assessment service"""
    service = RiskAssessmentService()
    
    # Test risk assessment
    print("Assessing risks for test farmer...")
    
    location = {"lat": 12.9716, "lon": 77.5946}
    
    assessment = await service.assess_farmer_risks(
        farmer_id="test_farmer_004",
        crop_name="rice",
        location=location,
        current_stage="vegetative"
    )
    
    print(f"\n✅ Risk assessment completed!")
    print(f"Assessment ID: {assessment.assessment_id}")
    print(f"Overall Risk Score: {assessment.risk_score:.2f}")
    print(f"Weather Risk Score: {assessment.weather_risk_score:.2f}")
    print(f"Pest Risk Score: {assessment.pest_risk_score:.2f}")
    print(f"Market Risk Score: {assessment.market_risk_score:.2f}")
    
    print(f"\nActive Risks ({len(assessment.active_risks)}):")
    for risk in assessment.active_risks:
        print(f"  {risk.title} - {risk.severity.value} - Score: {risk.risk_score:.2f}")
    
    print(f"\nImmediate Actions:")
    for action in assessment.immediate_actions:
        print(f"  • {action}")
    
    print(f"\nPreventive Measures:")
    for measure in assessment.preventive_measures[:3]:
        print(f"  • {measure}")
    
    print(f"\nInsurance Recommendations:")
    for rec in assessment.insurance_recommendations:
        print(f"  • {rec}")
    
    # Test alert generation
    print(f"\nGenerating immediate alerts...")
    alerts = await service.generate_alerts(assessment, "immediate")
    
    print(f"Generated {len(alerts)} immediate alerts:")
    for alert in alerts:
        print(f"  {alert.severity.value}: {alert.message}")
    
    # Export assessment
    export_success = service.export_assessment_to_json(assessment, "test_risk_assessment.json")
    print(f"\nAssessment Export: {'✅ Success' if export_success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_risk_assessment_service())
