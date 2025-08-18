"""
Crop Cycle API Router
Main API endpoints for crop cycle planning and tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel

# Import services
from app.services.crop_planning_engine import CropPlanningEngine, CropPlan
from app.services.crop_tracking_service import CropTrackingService, ProgressStatus, TaskStatus
from app.services.risk_assessment_service import RiskAssessmentService, RiskAssessment
from app.services.data_collection_coordinator import DataCollectionCoordinator, UnifiedFarmerData
from app.services.real_data_integration_service import RealDataIntegrationService

# Import existing models
from app.models import User, FarmerProfile, Season, CropCycle, GrowthStage, CropTask, CropObservation, RiskAlert, PlanStatus, Crop
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crop-cycle", tags=["crop-cycle"])

# Pydantic models for API requests/responses
class CropPlanRequest(BaseModel):
    target_crop: Optional[str] = None
    target_area: Optional[float] = None
    target_season: Optional[str] = None
    force_refresh: bool = False

class CropPlanResponse(BaseModel):
    plan_id: str
    crop_name: str
    crop_variety: str
    season: str
    area_acres: float
    status: str
    confidence_score: float
    expected_yield: float
    estimated_investment: float
    expected_revenue: float
    net_profit_estimate: float
    risk_level: str
    created_at: datetime

class TrackerRequest(BaseModel):
    plan_id: str
    crop_name: str
    crop_variety: str
    area_acres: float
    planting_date: date

class ProgressUpdateRequest(BaseModel):
    new_stage: str
    observation_notes: Optional[str] = None
    health_score: Optional[float] = None

class TaskUpdateRequest(BaseModel):
    task_id: str
    new_status: str
    completion_notes: Optional[str] = None

class RiskAssessmentResponse(BaseModel):
    assessment_id: str
    overall_risk_score: float
    weather_risk_score: float
    pest_risk_score: float
    market_risk_score: float
    active_risks_count: int
    immediate_actions: List[str]
    insurance_recommendations: List[str]

# Service instances
planning_engine = CropPlanningEngine()
tracking_service = CropTrackingService()
risk_service = RiskAssessmentService()
data_coordinator = DataCollectionCoordinator()
real_data_service = RealDataIntegrationService()

async def get_farmer_profile(db: AsyncSession, client_id: str) -> Optional[Dict[str, Any]]:
    """Get farmer profile from database"""
    try:
        # Fetch farmer profile from database
        profile = await db.get(FarmerProfile, client_id)
        if not profile:
            return None
        
        # Fetch user crop preferences
        from sqlmodel import select
        from app.models import UserCropPreference, Crop
        
        # Get crop preferences
        crop_prefs_result = await db.execute(
            select(UserCropPreference.crop_id, UserCropPreference.priority_score)
            .where(UserCropPreference.client_id == client_id)
            .order_by(UserCropPreference.priority_score.desc())
        )
        crop_prefs = crop_prefs_result.all()
        
        # Get crop names
        crop_ids = [pref[0] for pref in crop_prefs]  # pref[0] is crop_id
        if crop_ids:
            crops_result = await db.execute(
                select(Crop.name_en).where(Crop.id.in_(crop_ids))
            )
            crop_names = [crop.lower() for crop in crops_result.scalars().all()]
        else:
            crop_names = []
        
        # Build comprehensive farmer profile
        farmer_profile = {
            "client_id": profile.client_id,
            "pincode": profile.pincode,
            "lat": profile.lat,
            "lon": profile.lon,
            "district": None,  # Will be derived from pincode if needed
            "state": None,     # Will be derived from pincode if needed
            "farm_size": profile.farm_size,
            "experience_years": profile.experience_years,
            "irrigation_type": profile.irrigation_type,
            "soil_type": profile.soil_type,
            "crop_preferences": crop_names,
            "profile_data": profile
        }
        
        # If we have coordinates, we can derive district/state
        if profile.lat and profile.lon:
            # You could add geocoding here if needed
            pass
        elif profile.pincode:
            # You could add pincode to district/state mapping here if needed
            pass
        
        return farmer_profile
        
    except Exception as e:
        logger.error(f"Error fetching farmer profile for {client_id}: {e}")
        return None

@router.post("/plan", response_model=CropPlanResponse)
async def create_crop_plan(
    request: CropPlanRequest,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a comprehensive crop plan for the current farmer
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get farmer profile
        farmer_profile = await get_farmer_profile(db, client_id)
        if not farmer_profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        
        # Convert season string to enum
        target_season = None
        if request.target_season:
            try:
                target_season = Season(request.target_season.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid season. Use: kharif, rabi, zaid, summer")
        
        # Generate crop plan
        crop_plan = await planning_engine.generate_crop_plan(
            farmer_profile=farmer_profile,
            target_crop=request.target_crop,
            target_area=request.target_area,
            target_season=target_season,
            force_refresh=request.force_refresh
        )
        
        # Convert to response model
        response = CropPlanResponse(
            plan_id=crop_plan.plan_id,
            crop_name=crop_plan.crop_name,
            crop_variety=crop_plan.crop_variety,
            season=crop_plan.season.value,
            area_acres=crop_plan.area_acres,
            status=crop_plan.status.value,
            confidence_score=crop_plan.recommendation.confidence_score,
            expected_yield=crop_plan.recommendation.expected_yield_per_acre,
            estimated_investment=crop_plan.estimated_investment,
            expected_revenue=crop_plan.expected_revenue,
            net_profit_estimate=crop_plan.net_profit_estimate,
            risk_level=crop_plan.recommendation.risk_level.value,
            created_at=crop_plan.created_at
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating crop plan: {str(e)}")

@router.get("/plan/{plan_id}", response_model=Dict[str, Any])
async def get_crop_plan(
    plan_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed crop plan by ID
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get cached plan
        crop_plan = await planning_engine.get_cached_plan(plan_id)
        if not crop_plan:
            raise HTTPException(status_code=404, detail="Crop plan not found")
        
        # Verify the plan belongs to the requesting user
        if crop_plan.farmer_id != client_id:
            raise HTTPException(status_code=403, detail="Access denied to this crop plan")
        
        # Convert to dict for response
        plan_data = {
            "plan_id": crop_plan.plan_id,
            "farmer_id": crop_plan.farmer_id,
            "crop_name": crop_plan.crop_name,
            "crop_variety": crop_plan.crop_variety,
            "season": crop_plan.season.value,
            "area_acres": crop_plan.area_acres,
            "status": crop_plan.status.value,
            "recommendation": {
                "confidence_score": crop_plan.recommendation.confidence_score,
                "reasoning": crop_plan.recommendation.reasoning,
                "expected_yield_per_acre": crop_plan.recommendation.expected_yield_per_acre,
                "risk_level": crop_plan.recommendation.risk_level.value,
                "soil_suitability": crop_plan.recommendation.soil_suitability_score,
                "climate_suitability": crop_plan.recommendation.climate_suitability_score
            },
            "planting_schedule": {
                "optimal_planting_date": crop_plan.planting_schedule.optimal_planting_date.isoformat(),
                "planting_window_start": crop_plan.planting_schedule.planting_window_start.isoformat(),
                "planting_window_end": crop_plan.planting_schedule.planting_window_end.isoformat(),
                "critical_factors": crop_plan.planting_schedule.critical_factors,
                "preparation_tasks": crop_plan.planting_schedule.preparation_tasks
            },
            "resource_requirements": {
                "estimated_cost_per_acre": crop_plan.resource_requirements.estimated_cost_per_acre,
                "seeds_kg_per_acre": crop_plan.resource_requirements.seeds_kg_per_acre,
                "water_requirement_mm": crop_plan.resource_requirements.water_requirement_mm
            },
            "financial_planning": {
                "estimated_investment": crop_plan.estimated_investment,
                "expected_revenue": crop_plan.expected_revenue,
                "subsidy_benefits": crop_plan.subsidy_benefits,
                "net_profit_estimate": crop_plan.net_profit_estimate
            },
            "risk_assessment": {
                "risk_factors": crop_plan.risk_factors,
                "mitigation_strategies": crop_plan.mitigation_strategies,
                "insurance_recommendations": crop_plan.insurance_recommendations
            },
            "created_at": crop_plan.created_at.isoformat(),
            "updated_at": crop_plan.updated_at.isoformat()
        }
        
        return plan_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crop plan: {str(e)}")

@router.post("/tracker", response_model=Dict[str, Any])
async def create_crop_tracker(
    request: TrackerRequest,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a crop tracker for monitoring progress
    """
    try:
        # Create tracker
        tracker = await tracking_service.create_crop_tracker(
            plan_id=request.plan_id,
            farmer_id=current_user.client_id,
            crop_name=request.crop_name,
            crop_variety=request.crop_variety,
            area_acres=request.area_acres,
            planting_date=request.planting_date
        )
        
        # Convert to response format
        tracker_data = {
            "tracker_id": tracker.tracker_id,
            "plan_id": tracker.plan_id,
            "crop_name": tracker.crop_name,
            "crop_variety": tracker.crop_variety,
            "area_acres": tracker.area_acres,
            "planting_date": tracker.planting_date.isoformat(),
            "expected_harvest_date": tracker.expected_harvest_date.isoformat(),
            "current_stage": tracker.current_stage.value,
            "current_stage_name": tracker.current_stage_name,
            "days_since_planting": tracker.days_since_planting,
            "days_to_harvest": tracker.days_to_harvest,
            "overall_progress": tracker.overall_progress,
            "tasks_count": len(tracker.tasks),
            "created_at": tracker.created_at.isoformat()
        }
        
        return tracker_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating crop tracker: {str(e)}")

@router.put("/tracker/{tracker_id}/progress")
async def update_crop_progress(
    tracker_id: str,
    request: ProgressUpdateRequest,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update crop progress to a new stage
    """
    try:
        # Convert stage string to enum
        try:
            new_stage = ProgressStatus(request.new_stage.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid stage. Use: planted, germinated, vegetative, flowering, fruiting, maturing, ready_for_harvest, harvested")
        
        # Update progress
        updated_tracker = await tracking_service.update_crop_progress(
            tracker_id=tracker_id,
            new_stage=new_stage,
            observation_notes=request.observation_notes,
            health_score=request.health_score
        )
        
        return {
            "message": "Progress updated successfully",
            "tracker_id": tracker_id,
            "new_stage": updated_tracker.current_stage.value,
            "overall_progress": updated_tracker.overall_progress,
            "days_since_planting": updated_tracker.days_since_planting
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")

@router.put("/tracker/{tracker_id}/task/{task_id}")
async def update_task_status(
    tracker_id: str,
    task_id: str,
    request: TaskUpdateRequest,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update task status
    """
    try:
        # Convert status string to enum
        try:
            new_status = TaskStatus(request.new_status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status. Use: pending, in_progress, completed, overdue, skipped")
        
        # Update task
        success = await tracking_service.update_task_status(
            tracker_id=tracker_id,
            task_id=task_id,
            new_status=new_status,
            completion_notes=request.completion_notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "message": "Task status updated successfully",
            "task_id": task_id,
            "new_status": new_status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task status: {str(e)}")

@router.get("/tracker/{tracker_id}", response_model=Dict[str, Any])
async def get_crop_tracker(
    tracker_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed crop tracker information
    """
    try:
        # Get tracker
        tracker = await tracking_service.get_tracker(tracker_id)
        if not tracker:
            raise HTTPException(status_code=404, detail="Crop tracker not found")
        
        # Convert to response format
        tracker_data = {
            "tracker_id": tracker.tracker_id,
            "plan_id": tracker.plan_id,
            "crop_name": tracker.crop_name,
            "crop_variety": tracker.crop_variety,
            "area_acres": tracker.area_acres,
            "planting_date": tracker.planting_date.isoformat(),
            "expected_harvest_date": tracker.expected_harvest_date.isoformat(),
            "current_stage": tracker.current_stage.value,
            "current_stage_name": tracker.current_stage_name,
            "days_since_planting": tracker.days_since_planting,
            "days_to_harvest": tracker.days_to_harvest,
            "overall_progress": tracker.overall_progress,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "task_description": task.task_description,
                    "task_type": task.task_type,
                    "due_date": task.due_date.isoformat(),
                    "completed_date": task.completed_date.isoformat() if task.completed_date else None,
                    "status": task.status.value,
                    "priority": task.priority,
                    "notes": task.notes
                } for task in tracker.tasks
            ],
            "observations": [
                {
                    "observation_id": obs.observation_id,
                    "stage_name": obs.stage_name,
                    "observation_date": obs.observation_date.isoformat(),
                    "growth_percentage": obs.growth_percentage,
                    "health_score": obs.health_score,
                    "notes": obs.notes,
                    "next_expected_milestone": obs.next_expected_milestone,
                    "days_to_next_milestone": obs.days_to_next_milestone
                } for obs in tracker.observations
            ],
            "weather_alerts": tracker.weather_alerts,
            "irrigation_recommendations": tracker.irrigation_recommendations,
            "created_at": tracker.created_at.isoformat(),
            "updated_at": tracker.updated_at.isoformat()
        }
        
        return tracker_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crop tracker: {str(e)}")

@router.get("/tracker", response_model=List[Dict[str, Any]])
async def get_farmer_trackers(
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all crop trackers for the current farmer
    """
    try:
        # Get all trackers for farmer
        trackers = await tracking_service.get_farmer_trackers(client_id)
        
        # Convert to response format
        trackers_data = []
        for tracker in trackers:
            tracker_data = {
                "tracker_id": tracker.tracker_id,
                "plan_id": tracker.plan_id,
                "crop_name": tracker.crop_name,
                "crop_variety": tracker.crop_variety,
                "area_acres": tracker.area_acres,
                "planting_date": tracker.planting_date.isoformat(),
                "expected_harvest_date": tracker.expected_harvest_date.isoformat(),
                "current_stage": tracker.current_stage.value,
                "current_stage_name": tracker.current_stage_name,
                "overall_progress": tracker.overall_progress,
                "days_since_planting": tracker.days_since_planting,
                "days_to_harvest": tracker.days_to_harvest,
                "tasks_count": len(tracker.tasks),
                "observations_count": len(tracker.observations),
                "created_at": tracker.created_at.isoformat(),
                "updated_at": tracker.updated_at.isoformat()
            }
            trackers_data.append(tracker_data)
        
        return trackers_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trackers: {str(e)}")

@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_risks(
    crop_name: str = Body(...),
    location: Dict[str, float] = Body(...),
    current_stage: str = Body(...),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Assess risks for a specific crop and location
    """
    try:
        # Assess risks
        assessment = await risk_service.assess_farmer_risks(
            farmer_id=client_id,
            crop_name=crop_name,
            location=location,
            current_stage=current_stage
        )
        
        # Convert to response model
        response = RiskAssessmentResponse(
            assessment_id=assessment.assessment_id,
            overall_risk_score=assessment.risk_score,
            weather_risk_score=assessment.weather_risk_score,
            pest_risk_score=assessment.pest_risk_score,
            market_risk_score=assessment.market_risk_score,
            active_risks_count=len(assessment.active_risks),
            immediate_actions=assessment.immediate_actions,
            insurance_recommendations=assessment.insurance_recommendations
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing risks: {str(e)}")

@router.get("/data/{farmer_id}", response_model=Dict[str, Any])
async def get_farmer_data(
    farmer_id: str,
    force_refresh: bool = Query(False),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive farmer data from all sources
    """
    try:
        # Verify user has access to this data
        if client_id != farmer_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get farmer profile
        farmer_profile = await get_farmer_profile(get_db(), farmer_id)
        if not farmer_profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        
        # Collect comprehensive data using real data sources
        farmer_data = await real_data_service.get_comprehensive_farmer_data(
            farmer_profile, force_refresh
        )
        
        # Convert to response format
        data_response = {
            "farmer_id": farmer_data.farmer_id,
            "location": farmer_data.location,
            "pincode": farmer_data.pincode,
            "district": farmer_data.district,
            "state": farmer_data.state,
            "data_reliability_score": farmer_data.data_reliability_score,
            "last_updated": farmer_data.last_updated.isoformat(),
            "soil_health": {
                "available": farmer_data.soil_health is not None,
                "data": {
                    "soil_type": farmer_data.soil_health.soil_type,
                    "ph_level": farmer_data.soil_health.ph_level,
                    "organic_carbon": farmer_data.soil_health.organic_carbon,
                    "nitrogen_n": farmer_data.soil_health.nitrogen_n,
                    "phosphorus_p": farmer_data.soil_health.phosphorus_p,
                    "potassium_k": farmer_data.soil_health.potassium_k,
                    "source": farmer_data.soil_health.source
                } if farmer_data.soil_health else None
            },
            "crop_calendars": [
                {
                    "crop_name": cal.crop_name,
                    "crop_variety": cal.crop_variety,
                    "region": cal.region,
                    "season": cal.season.value,
                    "total_duration_days": cal.total_duration_days,
                    "source": cal.source
                } for cal in farmer_data.crop_calendars
            ],
            "eligible_schemes": [
                {
                    "scheme_name": scheme.scheme.scheme_name,
                    "category": scheme.scheme.category.value,
                    "match_score": scheme.match_score,
                    "application_status": scheme.application_status,
                    "estimated_benefit": scheme.estimated_benefit
                } for scheme in farmer_data.eligible_schemes
            ]
        }
        
        return data_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving farmer data: {str(e)}")

@router.get("/real-data/status")
async def get_real_data_status(
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of all real data sources
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get real data source status
        status = await real_data_service.get_data_source_status()
        
        return {
            "status": "success",
            "data_sources": status,
            "last_updated": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting real data status: {str(e)}")

@router.get("/real-data/weather/{latitude}/{longitude}")
async def get_real_weather_data(
    latitude: float,
    longitude: float,
    force_refresh: bool = Query(False),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time weather data for a location
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get real-time weather data
        weather_data = await real_data_service.get_real_time_weather(
            latitude, longitude, force_refresh
        )
        
        # Add validation to ensure weather_data is not None
        if weather_data is None:
            logger.error("Weather data is None from real_data_service")
            return {
                "status": "error",
                "message": "Failed to fetch weather data",
                "weather_data": {
                    "temperature": 0.0,
                    "humidity": 0.0,
                    "rainfall": 0.0,
                    "wind_speed": 0.0,
                    "weather_description": "Data unavailable",
                    "timestamp": datetime.now().isoformat(),
                    "location": {"lat": latitude, "lng": longitude}
                }
            }
        
        # Validate weather_data has required attributes
        try:
            return {
                "status": "success",
                "weather_data": {
                    "temperature": getattr(weather_data, 'temperature', 0.0),
                    "humidity": getattr(weather_data, 'humidity', 0.0),
                    "rainfall": getattr(weather_data, 'rainfall', 0.0),
                    "wind_speed": getattr(weather_data, 'wind_speed', 0.0),
                    "weather_description": getattr(weather_data, 'weather_description', 'Unknown'),
                    "timestamp": getattr(weather_data, 'timestamp', datetime.now()).isoformat(),
                    "location": getattr(weather_data, 'location', {"lat": latitude, "lng": longitude})
                }
            }
        except Exception as e:
            logger.error(f"Error formatting weather data: {e}")
            logger.error(f"Weather data type: {type(weather_data)}")
            logger.error(f"Weather data: {weather_data}")
            
            # Return fallback data
            return {
                "status": "error",
                "message": "Error formatting weather data",
                "weather_data": {
                    "temperature": 0.0,
                    "humidity": 0.0,
                    "rainfall": 0.0,
                    "wind_speed": 0.0,
                    "weather_description": "Data unavailable",
                    "timestamp": datetime.now().isoformat(),
                    "location": {"lat": latitude, "lng": longitude}
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weather data: {str(e)}")

@router.get("/real-data/weather/{latitude}/{longitude}/forecast")
async def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = Query(7, ge=1, le=14, description="Number of days for forecast"),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get weather forecast for a location
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get weather forecast
        forecast_data = await real_data_service.get_weather_forecast(
            latitude, longitude, days
        )
        
        # Validate forecast_data
        if forecast_data is None:
            logger.error("Forecast data is None from real_data_service")
            return {
                "status": "error",
                "message": "Failed to fetch forecast data",
                "forecast": [],
                "forecast_days": days,
                "timestamp": datetime.now().isoformat()
            }
        
        # Ensure forecast_data is a list
        if not isinstance(forecast_data, list):
            logger.error(f"Forecast data is not a list: {type(forecast_data)}")
            return {
                "status": "error",
                "message": "Invalid forecast data format",
                "forecast": [],
                "forecast_days": days,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "status": "success",
            "forecast": forecast_data,
            "forecast_days": days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weather forecast: {str(e)}")

@router.get("/real-data/market/{crop_name}")
async def get_real_market_data(
    crop_name: str,
    state: str = Query(None),
    district: str = Query(None),
    force_refresh: bool = Query(False),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time market data for a crop
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get real-time market data
        market_data = await real_data_service.get_real_time_market_data(
            crop_name, state, district, force_refresh
        )
        
        # Convert to response format
        market_response = []
        for data in market_data:
            market_response.append({
                "crop_name": data.crop_name,
                "mandi_name": data.mandi_name,
                "state": data.state,
                "district": data.district,
                "min_price": data.min_price,
                "max_price": data.max_price,
                "modal_price": data.modal_price,
                "date": data.date.isoformat(),
                "source": data.source
            })
        
        return {
            "status": "success",
            "crop_name": crop_name,
            "market_data": market_response,
            "total_markets": len(market_response),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting market data: {str(e)}")

@router.get("/real-data/market/{crop_name}/trends")
async def get_market_price_trends(
    crop_name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for trend analysis"),
    state: str = Query(None, description="State for market data"),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get market price trends for a crop
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get market price trends
        trends_data = await real_data_service.get_market_price_trends(
            crop_name, state, days
        )
        
        return {
            "status": "success",
            "crop_name": crop_name,
            "trends": trends_data,
            "analysis_period_days": days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting market trends: {str(e)}")

@router.get("/real-data/soil/{pincode}")
async def get_real_soil_data(
    pincode: str,
    force_refresh: bool = Query(False),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time soil data for a pincode
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get real-time soil data
        soil_data = await real_data_service.get_real_time_soil_data(pincode, force_refresh)
        
        if not soil_data:
            return {
                "status": "no_data",
                "message": f"No soil data found for pincode: {pincode}",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "status": "success",
            "soil_data": {
                "pincode": soil_data.pincode,
                "district": soil_data.district,
                "state": soil_data.state,
                "soil_type": soil_data.soil_type,
                "ph_level": soil_data.ph_level,
                "organic_carbon": soil_data.organic_carbon,
                "nitrogen_n": soil_data.nitrogen_n,
                "phosphorus_p": soil_data.phosphorus_p,
                "potassium_k": soil_data.potassium_k,
                "collected_date": soil_data.collected_date.isoformat(),
                "source": soil_data.source,
                "reliability_score": soil_data.reliability_score
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting soil data: {str(e)}")

@router.get("/export/plan/{plan_id}")
async def export_crop_plan(
    plan_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export crop plan in specified format
    """
    try:
        # Get cached plan
        crop_plan = await planning_engine.get_cached_plan(plan_id)
        if not crop_plan:
            raise HTTPException(status_code=404, detail="Crop plan not found")
        
        if format == "json":
            # Export to JSON
            filename = f"crop_plan_{plan_id}.json"
            success = planning_engine.export_plan_to_json(crop_plan, filename)
            
            if success:
                return {
                    "message": "Plan exported successfully",
                    "filename": filename,
                    "format": format
                }
            else:
                raise HTTPException(status_code=500, detail="Export failed")
        
        else:
            raise HTTPException(status_code=400, detail="CSV export not yet implemented")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting plan: {str(e)}")

@router.get("/export/tracker/{tracker_id}")
async def export_crop_tracker(
    tracker_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export crop tracker in specified format
    """
    try:
        # Get tracker
        tracker = await tracking_service.get_tracker(tracker_id)
        if not tracker:
            raise HTTPException(status_code=404, detail="Crop tracker not found")
        
        if format == "json":
            # Export to JSON
            filename = f"crop_tracker_{tracker_id}.json"
            success = tracking_service.export_tracker_to_json(tracker, filename)
            
            if success:
                return {
                    "message": "Tracker exported successfully",
                    "filename": filename,
                    "format": format
                }
            else:
                raise HTTPException(status_code=500, detail="Export failed")
        
        else:
            raise HTTPException(status_code=400, detail="CSV export not yet implemented")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting tracker: {str(e)}")

@router.post("/smart-checklist", response_model=List[Dict[str, Any]])
async def generate_smart_checklist(
    crop_name: str = Body(..., description="Name of the crop"),
    crop_variety: str = Body(..., description="Crop variety"),
    planting_date: str = Body(..., description="Planting date (YYYY-MM-DD)"),
    client_id: str = Query(..., description="Farmer's client ID"),
    include_weather: bool = Body(True, description="Include weather-based adjustments"),
    include_soil: bool = Body(True, description="Include soil-based customization"),
    include_market: bool = Body(True, description="Include market-based optimization"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate smart, personalized checklist for crop management
    
    This endpoint creates a comprehensive, AI-powered task list that considers:
    - Crop variety and growth requirements
    - Farmer's experience and farm characteristics
    - Weather conditions and forecasts
    - Soil health and conditions
    - Market trends and timing
    - Local agricultural practices
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get farmer profile
        farmer_profile = await get_farmer_profile(db, client_id)
        if not farmer_profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        
        # Parse planting date
        try:
            planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Prepare data sources for smart checklist
        weather_forecast = None
        soil_conditions = None
        market_conditions = None
        
        if include_weather:
            # TODO: Integrate with weather service
            weather_forecast = {
                "temperature": {"min": 20, "max": 35},
                "humidity": 65,
                "rainfall": 0,
                "wind_speed": 5
            }
        
        if include_soil:
            # TODO: Integrate with soil health service
            soil_conditions = {
                "ph_level": 6.5,
                "organic_matter": 2.5,
                "nitrogen_n": 80,
                "phosphorus_p": 25,
                "potassium_k": 150,
                "soil_type": "loam",
                "water_holding_capacity": 150
            }
        
        if include_market:
            # TODO: Integrate with market analysis service
            market_conditions = {
                "price_trend": "stable",
                "demand_forecast": "moderate",
                "storage_availability": "available"
            }
        
        # Generate smart checklist
        smart_tasks = await tracking_service.generate_smart_checklist(
            crop_name=crop_name,
            crop_variety=crop_variety,
            planting_date=planting_date_obj,
            farmer_profile=farmer_profile,
            weather_forecast=weather_forecast,
            soil_conditions=soil_conditions,
            market_conditions=market_conditions
        )
        
        # Convert to response format
        checklist_response = []
        for task in smart_tasks:
            task_data = {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "task_description": task.task_description,
                "task_type": task.task_type,
                "due_date": task.due_date.isoformat(),
                "priority": task.priority,
                "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
                "notes": task.notes,
                "assigned_to": task.assigned_to,
                "photos": task.photos or []
            }
            checklist_response.append(task_data)
        
        return checklist_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating smart checklist: {str(e)}")

# ============================================================================
# CRUD Endpoints for Crop Cycles
# ============================================================================

@router.get("/", response_model=List[Dict[str, Any]])
async def get_crop_cycles(
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all crop cycles for a farmer"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get farmer profile
        farmer_profile = await get_farmer_profile(db, client_id)
        if not farmer_profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        
        # Fetch actual crop cycles from database
        from sqlmodel import select
        
        # Query crop cycles for this client
        cycles_result = await db.execute(
            select(CropCycle).where(CropCycle.client_id == client_id)
        )
        cycles = cycles_result.scalars().all()
        
        logger.info(f"Found {len(cycles)} crop cycles for client {client_id}")
        
        # If no cycles found, return empty list instead of error
        if not cycles:
            logger.info(f"No crop cycles found for client {client_id}, returning empty list")
            return []
        
        # Helper function to safely handle photos field
        def safe_parse_photos(photos_field):
            """Safely parse photos field which might be string, list, or None"""
            if photos_field is None:
                return []
            elif isinstance(photos_field, str):
                try:
                    return photos_field.split(',') if photos_field.strip() else []
                except:
                    return []
            elif isinstance(photos_field, list):
                return photos_field
            else:
                return []
        
        # Helper function to safely handle enum values
        def safe_enum_value(enum_field, default_value):
            """Safely extract enum value or return default"""
            try:
                if enum_field and hasattr(enum_field, 'value'):
                    return enum_field.value
                else:
                    return default_value
            except:
                return default_value
        
        # Helper function to safely handle date fields
        def safe_date_format(date_field, default_value=""):
            """Safely format date field or return default"""
            try:
                if date_field and hasattr(date_field, 'isoformat'):
                    return date_field.isoformat()
                else:
                    return default_value
            except:
                return default_value
        
        # Convert to response format
        cycles_response = []
        for cycle in cycles:
            try:
                # Get associated crop information
                crop_result = await db.execute(
                    select(Crop).where(Crop.id == cycle.crop_id)
                )
                crop = crop_result.scalar_one_or_none()
                
                # Get associated tasks
                tasks_result = await db.execute(
                    select(CropTask).where(CropTask.cycle_id == cycle.id)
                )
                tasks = tasks_result.scalars().all()
                
                # Get associated growth stages
                stages_result = await db.execute(
                    select(GrowthStage).where(GrowthStage.cycle_id == cycle.id)
                )
                stages = stages_result.scalars().all()
                
                logger.info(f"Processing cycle {cycle.id}: crop={crop.id if crop else 'None'}, tasks={len(tasks)}, stages={len(stages)}")

                # Convert to frontend-compatible format
                cycle_data = {
                    "id": str(cycle.id) if cycle.id else "",
                    "clientId": str(cycle.client_id) if cycle.client_id else "",
                    "cropId": str(cycle.crop_id) if cycle.crop_id else "",
                    "variety": str(cycle.variety) if cycle.variety else "",
                    "startDate": safe_date_format(cycle.start_date),
                    "season": safe_enum_value(cycle.season, "kharif"),
                    "pincode": str(cycle.pincode) if cycle.pincode else "",
                    "lat": float(cycle.lat) if cycle.lat is not None else 0.0,
                    "lon": float(cycle.lon) if cycle.lon is not None else 0.0,
                    "irrigationType": str(cycle.irrigation_type) if cycle.irrigation_type else "",
                    "areaAcres": float(cycle.area_acres) if cycle.area_acres is not None else 0.0,
                    "language": str(cycle.language) if cycle.language else "en",
                    "status": safe_enum_value(cycle.status, "draft"),
                    "plannedHarvestDate": safe_date_format(cycle.planned_harvest_date),
                    "actualHarvestDate": safe_date_format(cycle.actual_harvest_date) if cycle.actual_harvest_date else None,
                    "createdAt": safe_date_format(cycle.created_at),
                    "updatedAt": safe_date_format(cycle.updated_at),
                    "crop": {
                        "id": str(crop.id) if crop and crop.id else str(cycle.crop_id) if cycle.crop_id else "",
                        "nameEn": str(crop.name_en) if crop and crop.name_en else "Unknown Crop",
                        "nameHi": str(crop.name_hi) if crop and crop.name_hi else "अज्ञात फसल",
                        "nameKn": str(crop.name_kn) if crop and crop.name_kn else "ಅಜ್ಞಾತ ಬೆಳೆ",
                        "category": "general",  # Default since Crop model doesn't have category
                        "growthDurationDays": 120,  # Default value
                        "season": safe_enum_value(cycle.season, "kharif"),
                        "region": "India",  # Default value
                        "description": "Crop from database",
                        "careInstructions": "Follow standard care practices",
                        "pestManagement": "Monitor for pests regularly",
                        "diseaseManagement": "Watch for common diseases",
                        "harvestingTips": "Harvest when ready",
                        "storageTips": "Store in cool, dry place",
                        "minTemperature": 20.0,  # Default values
                        "maxTemperature": 35.0,
                        "minRainfall": 500.0,
                        "maxRainfall": 1500.0,
                        "soilType": "Loamy",
                        "soilPhMin": 6.0,
                        "soilPhMax": 7.5,
                        "waterRequirement": "Moderate",
                        "fertilizerRequirement": "Balanced NPK",
                        "seedRate": "Standard rate",
                        "spacing": "Standard spacing",
                        "depth": "Standard depth",
                        "thinning": "Thin as needed",
                        "weeding": "Regular weeding",
                        "irrigation": "As needed",
                        "harvesting": "When mature",
                        "postHarvest": "Proper storage",
                        "marketDemand": "Stable",
                        "expectedYield": 2.5,
                        "unit": "tons/acre",
                        "minPrice": 1000.0,
                        "maxPrice": 2000.0,
                        "currency": "INR",
                        "imageUrl": "",
                        "createdAt": safe_date_format(cycle.created_at),
                        "updatedAt": safe_date_format(cycle.updated_at)
                    },
                    "growthStages": [
                        {
                            "id": str(stage.id) if stage.id else "",
                            "cycleId": str(stage.cycle_id) if stage.cycle_id else "",
                            "stageName": str(stage.stage_name) if stage.stage_name else "",
                            "expectedStartDate": safe_date_format(stage.expected_start_date),
                            "actualStartDate": safe_date_format(stage.actual_start_date) if stage.actual_start_date else None,
                            "expectedDurationDays": int(stage.expected_duration_days) if stage.expected_duration_days is not None else 0,
                            "progressPercentage": float(stage.progress_percentage) if stage.progress_percentage is not None else 0.0,
                            "notes": str(stage.notes) if stage.notes is not None else "",
                            "photos": safe_parse_photos(stage.photos),
                            "createdAt": safe_date_format(stage.created_at)
                        }
                        for stage in stages
                    ],
                    "tasks": [
                        {
                            "id": str(task.id) if task.id else "",
                            "cycleId": str(task.cycle_id) if task.cycle_id else "",
                            "title": str(task.task_name) if task.task_name else "",
                            "description": str(task.task_description) if task.task_description else "",
                            "taskType": str(task.task_type) if task.task_type else "",
                            "dueDate": safe_date_format(task.due_date),
                            "completedDate": safe_date_format(task.completed_date) if task.completed_date else None,
                            "status": safe_enum_value(task.status, "pending"),
                            "priority": str(task.priority) if task.priority else "medium",
                            "notes": str(task.notes) if task.notes is not None else "",
                            "photos": safe_parse_photos(task.photos),
                            "createdAt": safe_date_format(task.created_at)
                        }
                        for task in tasks
                    ]
                }
                
                # Debug logging to check data structure
                logger.info(f"Cycle data structure: {type(cycle_data)}")
                logger.info(f"Cycle data keys: {list(cycle_data.keys()) if isinstance(cycle_data, dict) else 'Not a dict'}")
                
                cycles_response.append(cycle_data)
            
            except Exception as e:
                logger.error(f"Error processing cycle {cycle.id if cycle else 'Unknown'}: {e}")
                # Skip this cycle and continue with others
                continue
        
        logger.info(f"Successfully processed {len(cycles_response)} crop cycles")
        return cycles_response
        
    except Exception as e:
        logger.error(f"Error fetching crop cycles: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching crop cycles: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "crop-cycle-api"
    }

@router.get("/debug/{client_id}")
async def debug_crop_cycles(
    client_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to check raw data structure"""
    try:
        # Get raw crop cycles
        from sqlmodel import select
        cycles_result = await db.execute(
            select(CropCycle).where(CropCycle.client_id == client_id)
        )
        cycles = cycles_result.scalars().all()
        
        debug_data = []
        for cycle in cycles:
            cycle_debug = {
                "id": str(cycle.id) if cycle.id else None,
                "client_id": str(cycle.client_id) if cycle.client_id else None,
                "crop_id": str(cycle.crop_id) if cycle.crop_id else None,
                "variety": str(cycle.variety) if cycle.variety else None,
                "start_date": cycle.start_date.isoformat() if cycle.start_date else None,
                "season": str(cycle.season) if cycle.season else None,
                "season_type": type(cycle.season).__name__ if cycle.season else None,
                "pincode": str(cycle.pincode) if cycle.pincode else None,
                "lat": float(cycle.lat) if cycle.lat is not None else None,
                "lon": float(cycle.lon) if cycle.lon is not None else None,
                "irrigation_type": str(cycle.irrigation_type) if cycle.irrigation_type else None,
                "area_acres": float(cycle.area_acres) if cycle.area_acres is not None else None,
                "language": str(cycle.language) if cycle.language else None,
                "status": str(cycle.status) if cycle.status else None,
                "status_type": type(cycle.status).__name__ if cycle.status else None,
                "planned_harvest_date": cycle.planned_harvest_date.isoformat() if cycle.planned_harvest_date else None,
                "actual_harvest_date": cycle.actual_harvest_date.isoformat() if cycle.actual_harvest_date else None,
                "created_at": cycle.created_at.isoformat() if cycle.created_at else None,
                "updated_at": cycle.updated_at.isoformat() if cycle.updated_at else None,
            }
            debug_data.append(cycle_debug)
        
        return {
            "client_id": client_id,
            "total_cycles": len(debug_data),
            "debug_data": debug_data
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        return {
            "error": str(e),
            "traceback": str(e.__traceback__)
        }

@router.post("/", response_model=Dict[str, Any])
async def create_crop_cycle(
    cycle_data: Dict[str, Any] = Body(...),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get farmer profile
        farmer_profile = await get_farmer_profile(db, client_id)
        if not farmer_profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        
        # Create actual crop cycle in database
        from sqlmodel import select
        import uuid
        
        # Generate unique ID for the crop cycle
        cycle_id = str(uuid.uuid4())
        
        # Parse dates - handle both date and datetime formats
        def parse_date(date_string):
            """Parse date string, handling both YYYY-MM-DD and ISO datetime formats"""
            if not date_string:
                return datetime.now().date()
            
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            # If all formats fail, raise error
            raise ValueError(f"Unable to parse date: {date_string}")
        
        start_date = parse_date(cycle_data.get("startDate"))
        planned_harvest_date = parse_date(cycle_data.get("plannedHarvestDate"))
        
        # Create new crop cycle
        new_cycle = CropCycle(
            id=cycle_id,
            client_id=client_id,
            crop_id=cycle_data.get("cropId"),
            variety=cycle_data.get("variety", "Standard"),
            start_date=start_date,
            season=Season(cycle_data.get("season", "kharif")),
            pincode=cycle_data.get("pincode", "560001"),
            lat=cycle_data.get("lat", 12.9716),
            lon=cycle_data.get("lon", 77.5946),
            irrigation_type=cycle_data.get("irrigationType", "drip"),
            area_acres=cycle_data.get("areaAcres", 2.5),
            language=cycle_data.get("language", "en"),
            status=PlanStatus.ACTIVE,
            planned_harvest_date=planned_harvest_date,
            actual_harvest_date=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(new_cycle)
        await db.commit()
        await db.refresh(new_cycle)
        
        # Get associated crop information
        crop_result = await db.execute(
            select(Crop).where(Crop.id == new_cycle.crop_id)
        )
        crop = crop_result.scalar_one_or_none()
        
        # Convert to response format
        cycle_response = {
            "id": new_cycle.id,
            "clientId": new_cycle.client_id,
            "cropId": new_cycle.crop_id,
            "variety": new_cycle.variety,
            "startDate": new_cycle.start_date.isoformat(),
            "season": new_cycle.season.value,
            "pincode": new_cycle.pincode,
            "lat": new_cycle.lat,
            "lon": new_cycle.lon,
            "irrigationType": new_cycle.irrigation_type,
            "areaAcres": new_cycle.area_acres,
            "language": new_cycle.language,
            "status": new_cycle.status.value,
            "plannedHarvestDate": new_cycle.planned_harvest_date.isoformat(),
            "actualHarvestDate": new_cycle.actual_harvest_date.isoformat() if new_cycle.actual_harvest_date else None,
            "createdAt": new_cycle.created_at.isoformat(),
            "updatedAt": new_cycle.updated_at.isoformat(),
            "crop": {
                "id": crop.id if crop else new_cycle.crop_id,
                "nameEn": crop.name_en if crop else "Unknown Crop",
                "nameHi": crop.name_hi if crop else "अज्ञात फसल",
                "nameKn": crop.name_kn if crop else "ಅಜ್ಞಾತ ಬೆಳೆ",
                "category": "general",
                "growthDurationDays": 120,
                "season": new_cycle.season.value,
                "region": "India",
                "description": "Crop from database",
                "careInstructions": "Follow standard care practices",
                "pestManagement": "Monitor for pests regularly",
                "diseaseManagement": "Watch for common diseases",
                "harvestingTips": "Harvest when ready",
                "storageTips": "Store in cool, dry place",
                "minTemperature": 20.0,
                "maxTemperature": 35.0,
                "minRainfall": 500.0,
                "maxRainfall": 1500.0,
                "soilType": "Loamy",
                "soilPhMin": 6.0,
                "soilPhMax": 7.5,
                "waterRequirement": "Moderate",
                "fertilizerRequirement": "Balanced NPK",
                "seedRate": "Standard rate",
                "spacing": "Standard spacing",
                "depth": "Standard depth",
                "thinning": "Thin as needed",
                "weeding": "Regular weeding",
                "irrigation": "As needed",
                "harvesting": "When mature",
                "postHarvest": "Proper storage",
                "marketDemand": "Stable",
                "expectedYield": 2.5,
                "unit": "tons/acre",
                "minPrice": 1000.0,
                "maxPrice": 2000.0,
                "currency": "INR",
                "imageUrl": "",
                "createdAt": new_cycle.created_at.isoformat(),
                "updatedAt": new_cycle.updated_at.isoformat()
            },
            "growthStages": [],
            "tasks": []
        }
        
        return cycle_response
        
    except Exception as e:
        logger.error(f"Error creating crop cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating crop cycle: {str(e)}")

@router.get("/{cycle_id}", response_model=Dict[str, Any])
async def get_crop_cycle(
    cycle_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Fetch actual crop cycle from database
        from sqlmodel import select
        
        # Query the specific crop cycle
        cycle_result = await db.execute(
            select(CropCycle).where(CropCycle.id == cycle_id, CropCycle.client_id == client_id)
        )
        cycle = cycle_result.scalar_one_or_none()
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        
        # Get associated crop information
        crop_result = await db.execute(
            select(Crop).where(Crop.id == cycle.crop_id)
        )
        crop = crop_result.scalar_one_or_none()
        
        # Get associated tasks
        tasks_result = await db.execute(
            select(CropTask).where(CropTask.cycle_id == cycle.id)
        )
        tasks = tasks_result.scalars().all()
        
        # Get associated growth stages
        stages_result = await db.execute(
            select(GrowthStage).where(GrowthStage.cycle_id == cycle.id)
        )
        stages = stages_result.scalars().all()
        
        # Convert to response format
        cycle_response = {
            "id": cycle.id,
            "clientId": cycle.client_id,
            "cropId": cycle.crop_id,
            "variety": cycle.variety,
            "startDate": cycle.start_date.isoformat(),
            "season": cycle.season.value,
            "pincode": cycle.pincode,
            "lat": cycle.lat,
            "lon": cycle.lon,
            "irrigationType": cycle.irrigation_type,
            "areaAcres": cycle.area_acres,
            "language": cycle.language,
            "status": cycle.status.value,
            "plannedHarvestDate": cycle.planned_harvest_date.isoformat(),
            "actualHarvestDate": cycle.actual_harvest_date.isoformat() if cycle.actual_harvest_date else None,
            "createdAt": cycle.created_at.isoformat(),
            "updatedAt": cycle.updated_at.isoformat(),
            "crop": {
                "id": crop.id if crop else cycle.crop_id,
                "nameEn": crop.name_en if crop else "Unknown Crop",
                "nameHi": crop.name_hi if crop else "अज्ञात फसल",
                "nameKn": crop.name_kn if crop else "ಅಜ್ಞಾತ ಬೆಳೆ",
                "category": "general",
                "growthDurationDays": 120,
                "season": cycle.season.value,
                "region": "India",
                "description": "Crop from database",
                "careInstructions": "Follow standard care practices",
                "pestManagement": "Monitor for pests regularly",
                "diseaseManagement": "Watch for common diseases",
                "harvestingTips": "Harvest when ready",
                "storageTips": "Store in cool, dry place",
                "minTemperature": 20.0,
                "maxTemperature": 35.0,
                "minRainfall": 500.0,
                "maxRainfall": 1500.0,
                "soilType": "Loamy",
                "soilPhMin": 6.0,
                "soilPhMax": 7.5,
                "waterRequirement": "Moderate",
                "fertilizerRequirement": "Balanced NPK",
                "seedRate": "Standard rate",
                "spacing": "Standard spacing",
                "depth": "Standard depth",
                "thinning": "Thin as needed",
                "weeding": "Regular weeding",
                "irrigation": "As needed",
                "harvesting": "When mature",
                "postHarvest": "Proper storage",
                "marketDemand": "Stable",
                "expectedYield": 2.5,
                "unit": "tons/acre",
                "minPrice": 1000.0,
                "maxPrice": 2000.0,
                "currency": "INR",
                "imageUrl": "",
                "createdAt": cycle.created_at.isoformat(),
                "updatedAt": cycle.updated_at.isoformat()
            },
            "growthStages": [
                {
                    "id": stage.id,
                    "cycleId": stage.cycle_id,
                    "stageName": stage.stage_name,
                    "expectedStartDate": stage.expected_start_date.isoformat(),
                    "actualStartDate": stage.actual_start_date.isoformat() if stage.actual_start_date else None,
                    "expectedDurationDays": stage.expected_duration_days,
                    "progressPercentage": stage.progress_percentage,
                    "notes": stage.notes,
                    "photos": stage.photos,
                    "createdAt": stage.created_at.isoformat()
                }
                for stage in stages
            ],
            "tasks": [
                {
                    "id": task.id,
                    "cycleId": task.cycle_id,
                    "taskName": task.task_name,
                    "taskDescription": task.task_description,
                    "taskType": task.task_type,
                    "dueDate": task.due_date.isoformat(),
                    "completedDate": task.completed_date.isoformat() if task.completed_date else None,
                    "status": task.status.value,
                    "priority": task.priority,
                    "notes": task.notes,
                    "photos": task.photos,
                    "createdAt": task.created_at.isoformat()
                }
                for task in tasks
            ]
        }
        
        return cycle_response
        
    except Exception as e:
        logger.error(f"Error fetching crop cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching crop cycle: {str(e)}")

@router.put("/{cycle_id}", response_model=Dict[str, Any])
async def update_crop_cycle(
    cycle_id: str,
    cycle_data: Dict[str, Any] = Body(...),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update actual crop cycle in database
        from sqlmodel import select
        
        # Query the specific crop cycle
        cycle_result = await db.execute(
            select(CropCycle).where(CropCycle.id == cycle_id, CropCycle.client_id == client_id)
        )
        cycle = cycle_result.scalar_one_or_none()
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        
        # Update fields if provided
        if "variety" in cycle_data:
            cycle.variety = cycle_data["variety"]
        if "startDate" in cycle_data:
            cycle.start_date = datetime.strptime(cycle_data["startDate"], "%Y-%m-%d").date()
        if "season" in cycle_data:
            cycle.season = Season(cycle_data["season"])
        if "pincode" in cycle_data:
            cycle.pincode = cycle_data["pincode"]
        if "lat" in cycle_data:
            cycle.lat = cycle_data["lat"]
        if "lon" in cycle_data:
            cycle.lon = cycle_data["lon"]
        if "irrigationType" in cycle_data:
            cycle.irrigation_type = cycle_data["irrigationType"]
        if "areaAcres" in cycle_data:
            cycle.area_acres = cycle_data["areaAcres"]
        if "language" in cycle_data:
            cycle.language = cycle_data["language"]
        if "status" in cycle_data:
            cycle.status = PlanStatus(cycle_data["status"])
        if "plannedHarvestDate" in cycle_data:
            cycle.planned_harvest_date = datetime.strptime(cycle_data["plannedHarvestDate"], "%Y-%m-%d").date()
        if "actualHarvestDate" in cycle_data:
            cycle.actual_harvest_date = datetime.strptime(cycle_data["actualHarvestDate"], "%Y-%m-%d").date()
        
        # Update timestamp
        cycle.updated_at = datetime.utcnow()
        
        # Commit changes
        await db.commit()
        await db.refresh(cycle)
        
        # Get associated crop information
        crop_result = await db.execute(
            select(Crop).where(Crop.id == cycle.crop_id)
        )
        crop = crop_result.scalar_one_or_none()
        
        # Convert to response format
        cycle_response = {
            "id": cycle.id,
            "clientId": cycle.client_id,
            "cropId": cycle.crop_id,
            "variety": cycle.variety,
            "startDate": cycle.start_date.isoformat(),
            "season": cycle.season.value,
            "pincode": cycle.pincode,
            "lat": cycle.lat,
            "lon": cycle.lon,
            "irrigationType": cycle.irrigation_type,
            "areaAcres": cycle.area_acres,
            "language": cycle.language,
            "status": cycle.status.value,
            "plannedHarvestDate": cycle.planned_harvest_date.isoformat(),
            "actualHarvestDate": cycle.actual_harvest_date.isoformat() if cycle.actual_harvest_date else None,
            "createdAt": cycle.created_at.isoformat(),
            "updatedAt": cycle.updated_at.isoformat(),
            "crop": {
                "id": crop.id if crop else cycle.crop_id,
                "nameEn": crop.name_en if crop else "Unknown Crop",
                "nameHi": crop.name_hi if crop else "अज्ञात फसल",
                "nameKn": crop.name_kn if crop else "ಅಜ್ಞಾತ ಬೆಳೆ",
                "category": "general",
                "growthDurationDays": 120,
                "season": cycle.season.value,
                "region": "India",
                "description": "Crop from database",
                "careInstructions": "Follow standard care practices",
                "pestManagement": "Monitor for pests regularly",
                "diseaseManagement": "Watch for common diseases",
                "harvestingTips": "Harvest when ready",
                "storageTips": "Store in cool, dry place",
                "minTemperature": 20.0,
                "maxTemperature": 35.0,
                "minRainfall": 500.0,
                "maxRainfall": 1500.0,
                "soilType": "Loamy",
                "soilPhMin": 6.0,
                "soilPhMax": 7.5,
                "waterRequirement": "Moderate",
                "fertilizerRequirement": "Balanced NPK",
                "seedRate": "Standard rate",
                "spacing": "Standard spacing",
                "depth": "Standard depth",
                "thinning": "Thin as needed",
                "weeding": "Regular weeding",
                "irrigation": "As needed",
                "harvesting": "When mature",
                "postHarvest": "Proper storage",
                "marketDemand": "Stable",
                "expectedYield": 2.5,
                "unit": "tons/acre",
                "minPrice": 1000.0,
                "maxPrice": 2000.0,
                "currency": "INR",
                "imageUrl": "",
                "createdAt": cycle.created_at.isoformat(),
                "updatedAt": cycle.updated_at.isoformat()
            }
        }
        
        return cycle_response
        
    except Exception as e:
        logger.error(f"Error updating crop cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating crop cycle: {str(e)}")

@router.delete("/{cycle_id}")
async def delete_crop_cycle(
    cycle_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete actual crop cycle from database
        from sqlmodel import select
        
        # Query the specific crop cycle
        cycle_result = await db.execute(
            select(CropCycle).where(CropCycle.id == cycle_id, CropCycle.client_id == client_id)
        )
        cycle = cycle_result.scalar_one_or_none()
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Crop cycle not found")
        
        # Delete associated tasks first
        tasks_result = await db.execute(
            select(CropTask).where(CropTask.cycle_id == cycle_id)
        )
        tasks = tasks_result.scalars().all()
        for task in tasks:
            await db.delete(task)
        
        # Delete associated growth stages
        stages_result = await db.execute(
            select(GrowthStage).where(GrowthStage.cycle_id == cycle_id)
        )
        stages = stages_result.scalars().all()
        for stage in stages:
            await db.delete(stage)
        
        # Delete associated observations
        observations_result = await db.execute(
            select(CropObservation).where(CropObservation.cycle_id == cycle_id)
        )
        observations = observations_result.scalars().all()
        for observation in observations:
            await db.delete(observation)
        
        # Delete associated risk alerts
        risks_result = await db.execute(
            select(RiskAlert).where(RiskAlert.cycle_id == cycle_id)
        )
        risks = risks_result.scalars().all()
        for risk in risks:
            await db.delete(risk)
        
        # Delete the crop cycle
        await db.delete(cycle)
        await db.commit()
        
        return {"message": "Crop cycle deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting crop cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting crop cycle: {str(e)}")

# ============================================================================
# Task Management Endpoints
# ============================================================================

@router.get("/{cycle_id}/tasks", response_model=List[Dict[str, Any]])
async def get_crop_cycle_tasks(
    cycle_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Fetch actual tasks from database
        from sqlmodel import select
        
        # Query tasks for this crop cycle
        tasks_result = await db.execute(
            select(CropTask).where(CropTask.cycle_id == cycle_id)
        )
        tasks = tasks_result.scalars().all()
        
        # Convert to response format
        tasks_response = []
        for task in tasks:
            task_data = {
                "id": task.id,
                "cycleId": task.cycle_id,
                "taskName": task.task_name,
                "taskDescription": task.task_description,
                "taskType": task.task_type,
                "dueDate": task.due_date.isoformat(),
                "completedDate": task.completed_date.isoformat() if task.completed_date else None,
                "status": task.status.value,
                "priority": task.priority,
                "notes": task.notes,
                "photos": task.photos,
                "createdAt": task.created_at.isoformat()
            }
            tasks_response.append(task_data)
        
        return tasks_response
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")

@router.post("/{cycle_id}/tasks", response_model=Dict[str, Any])
async def create_crop_cycle_task(
    cycle_id: str,
    task_data: Dict[str, Any] = Body(...),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create actual task in database
        import uuid
        
        # Generate unique ID for the task
        task_id = str(uuid.uuid4())
        
        # Parse due date - handle both date and datetime formats
        def parse_date(date_string):
            """Parse date string, handling both YYYY-MM-DD and ISO datetime formats"""
            if not date_string:
                return datetime.now().date()
            
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            # If all formats fail, raise error
            raise ValueError(f"Unable to parse date: {date_string}")
        
        due_date = parse_date(task_data.get("dueDate"))
        
        # Create new task
        new_task = CropTask(
            id=task_id,
            cycle_id=cycle_id,
            task_name=task_data.get("title", "New Task"),
            task_description=task_data.get("description", "Task description"),
            task_type=task_data.get("taskType", "action"),
            due_date=due_date,
            completed_date=None,
            status=TaskStatus.PENDING.value,
            priority=task_data.get("priority", "medium"),
            notes=task_data.get("notes"),
            photos=task_data.get("photos"),
            created_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        
        # Convert to response format
        task_response = {
            "id": new_task.id,
            "cycleId": new_task.cycle_id,
            "taskName": new_task.task_name,
            "taskDescription": new_task.task_description,
            "taskType": new_task.task_type,
            "dueDate": new_task.due_date.isoformat(),
            "completedDate": new_task.completed_date.isoformat() if new_task.completed_date else None,
            "status": new_task.status.value,
            "priority": new_task.priority,
            "notes": new_task.notes,
            "photos": new_task.photos,
            "createdAt": new_task.created_at.isoformat()
        }
        
        return task_response
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@router.put("/{cycle_id}/tasks/{task_id}", response_model=Dict[str, Any])
async def update_crop_cycle_task(
    cycle_id: str,
    task_id: str,
    task_data: Dict[str, Any] = Body(...),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Update a task for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update actual task in database
        from sqlmodel import select
        
        # Query the specific task
        task_result = await db.execute(
            select(CropTask).where(CropTask.id == task_id, CropTask.cycle_id == cycle_id)
        )
        task = task_result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update fields if provided
        if "title" in task_data:
            task.task_name = task_data["title"]
        if "description" in task_data:
            task.task_description = task_data["description"]
        if "taskType" in task_data:
            task.task_type = task_data["taskType"]
        if "dueDate" in task_data:
            task.due_date = datetime.strptime(task_data["dueDate"], "%Y-%m-%d").date()
        if "priority" in task_data:
            task.priority = task_data["priority"]
        if "status" in task_data:
            task.status = TaskStatus(task_data["status"])
        if "notes" in task_data:
            task.notes = task_data["notes"]
        if "photos" in task_data:
            task.photos = task_data["photos"]
        
        # Commit changes
        await db.commit()
        await db.refresh(task)
        
        # Convert to response format
        task_response = {
            "id": task.id,
            "cycleId": task.cycle_id,
            "taskName": task.task_name,
            "taskDescription": task.task_description,
            "taskType": task.task_type,
            "dueDate": task.due_date.isoformat(),
            "completedDate": task.completed_date.isoformat() if task.completed_date else None,
            "status": task.status.value,
            "priority": task.priority,
            "notes": task.notes,
            "photos": task.photos,
            "createdAt": task.created_at.isoformat()
        }
        
        return task_response
        
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@router.delete("/{cycle_id}/tasks/{task_id}")
async def delete_crop_cycle_task(
    cycle_id: str,
    task_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete actual task from database
        from sqlmodel import select
        
        # Query the specific task
        task_result = await db.execute(
            select(CropTask).where(CropTask.id == task_id, CropTask.cycle_id == cycle_id)
        )
        task = task_result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete the task
        await db.delete(task)
        await db.commit()
        
        return {"message": "Task deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

# ============================================================================
# Observation and Risk Endpoints
# ============================================================================

@router.get("/{cycle_id}/observations", response_model=List[Dict[str, Any]])
async def get_crop_cycle_observations(
    cycle_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all observations for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Fetch actual observations from database
        from sqlmodel import select
        
        # Query observations for this crop cycle
        observations_result = await db.execute(
            select(CropObservation).where(CropObservation.cycle_id == cycle_id)
        )
        observations = observations_result.scalars().all()
        
        # Convert to response format
        observations_response = []
        for observation in observations:
            observation_data = {
                "id": observation.id,
                "cycleId": observation.cycle_id,
                "stageName": observation.stage_name,
                "observationDate": observation.observation_date.isoformat(),
                "growthPercentage": observation.growth_percentage,
                "healthScore": observation.health_score,
                "observations": observation.observations,
                "photos": observation.photos,
                "weatherConditions": observation.weather_conditions,
                "notes": observation.notes,
                "nextExpectedMilestone": observation.next_expected_milestone,
                "daysToNextMilestone": observation.days_to_next_milestone,
                "createdAt": observation.created_at.isoformat()
            }
            observations_response.append(observation_data)
        
        return observations_response
        
    except Exception as e:
        logger.error(f"Error fetching observations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching observations: {str(e)}")

@router.post("/{cycle_id}/observations", response_model=Dict[str, Any])
async def create_crop_cycle_observation(
    cycle_id: str,
    observation_data: Dict[str, Any] = Body(...),
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Create a new observation for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create actual observation in database
        import uuid
        
        # Generate unique ID for the observation
        observation_id = str(uuid.uuid4())
        
        # Parse observation date - handle both date and datetime formats
        def parse_date(date_string):
            """Parse date string, handling both YYYY-MM-DD and ISO datetime formats"""
            if not date_string:
                return datetime.now().date()
            
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            # If all formats fail, raise error
            raise ValueError(f"Unable to parse date: {date_string}")
        
        observation_date = parse_date(observation_data.get("observationDate"))
        
        # Create new observation
        new_observation = CropObservation(
            id=observation_id,
            cycle_id=cycle_id,
            stage_name=observation_data.get("stageName", "general"),
            observation_date=observation_date,
            growth_percentage=observation_data.get("growthPercentage", 0.0),
            health_score=observation_data.get("healthScore", 5.0),
            observations=observation_data.get("observations"),
            photos=observation_data.get("photos"),
            weather_conditions=observation_data.get("weatherConditions"),
            notes=observation_data.get("notes", "Observation notes"),
            next_expected_milestone=observation_data.get("nextExpectedMilestone", "Continue monitoring"),
            days_to_next_milestone=observation_data.get("daysToNextMilestone", 7),
            created_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(new_observation)
        await db.commit()
        await db.refresh(new_observation)
        
        # Convert to response format
        observation_response = {
            "id": new_observation.id,
            "cycleId": new_observation.cycle_id,
            "stageName": new_observation.stage_name,
            "observationDate": new_observation.observation_date.isoformat(),
            "growthPercentage": new_observation.growth_percentage,
            "healthScore": new_observation.health_score,
            "observations": new_observation.observations,
            "photos": new_observation.photos,
            "weatherConditions": new_observation.weather_conditions,
            "notes": new_observation.notes,
            "nextExpectedMilestone": new_observation.next_expected_milestone,
            "daysToNextMilestone": new_observation.days_to_next_milestone,
            "createdAt": new_observation.created_at.isoformat()
        }
        
        return observation_response
        
    except Exception as e:
        logger.error(f"Error creating observation: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating observation: {str(e)}")

@router.get("/{cycle_id}/risks", response_model=List[Dict[str, Any]])
async def get_crop_cycle_risks(
    cycle_id: str,
    client_id: str = Query(..., description="Farmer's client ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get all risks for a crop cycle"""
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Fetch actual risks from database
        from sqlmodel import select
        
        # Query risks for this crop cycle
        risks_result = await db.execute(
            select(RiskAlert).where(RiskAlert.cycle_id == cycle_id, RiskAlert.is_active == True)
        )
        risks = risks_result.scalars().all()
        
        # Convert to response format
        risks_response = []
        for risk in risks:
            risk_data = {
                "id": risk.id,
                "cycleId": risk.cycle_id,
                "alertType": risk.alert_type,
                "severity": risk.severity,
                "title": risk.title,
                "message": risk.message,
                "riskScore": risk.risk_score,
                "mitigationStrategies": risk.mitigation_strategies,
                "isActive": risk.is_active,
                "createdAt": risk.created_at.isoformat(),
                "readAt": risk.read_at.isoformat() if risk.read_at else None
            }
            risks_response.append(risk_data)
        
        return risks_response
        
    except Exception as e:
        logger.error(f"Error fetching risks: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching risks: {str(e)}")

# ============================================================================
# AI-Powered Real-Time Recommendations
# ============================================================================

@router.post("/ai-recommendations", response_model=List[Dict[str, Any]])
async def get_ai_recommendations(
    client_id: str = Query(..., description="Farmer's client ID"),
    include_weather: bool = Body(True, description="Include weather-based recommendations"),
    include_market: bool = Body(True, description="Include market-based recommendations"),
    include_soil: bool = Body(True, description="Include soil-based recommendations"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time AI-powered farming recommendations
    
    This endpoint provides intelligent, context-aware recommendations by:
    - Analyzing real-time weather conditions
    - Monitoring market prices and trends
    - Assessing soil health and conditions
    - Tracking crop growth stages
    - Generating personalized action items
    
    The system uses LLM integration to provide natural language recommendations
    and prioritizes actions based on urgency and impact.
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get farmer profile for location data
        farmer_profile = await get_farmer_profile(db, client_id)
        if not farmer_profile:
            raise HTTPException(status_code=404, detail="Farmer profile not found")
        
        # Get location data
        location = {
            "lat": farmer_profile.get("lat", 12.9716),  # Default to Bangalore
            "lon": farmer_profile.get("lon", 77.5946),
            "pincode": farmer_profile.get("pincode")
        }
        
        # Get active crop cycles
        from sqlmodel import select
        
        cycles_result = await db.execute(
            select(CropCycle).where(CropCycle.client_id == client_id, CropCycle.status != "completed")
        )
        crop_cycles = cycles_result.scalars().all()
        
        # Convert crop cycles to dict format for the service
        cycles_data = []
        for cycle in crop_cycles:
            cycle_dict = {
                "id": cycle.id,
                "crop": {"nameEn": cycle.crop_name} if cycle.crop_name else None,
                "variety": cycle.variety,
                "currentStage": cycle.current_stage,
                "startDate": cycle.start_date,
                "tasks": []
            }
            
            # Get tasks for this cycle
            tasks_result = await db.execute(
                select(CropTask).where(CropTask.cycle_id == cycle.id)
            )
            tasks = tasks_result.scalars().all()
            
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "taskName": task.task_name,
                    "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
                    "dueDate": task.due_date.isoformat() if task.due_date else None
                }
                cycle_dict["tasks"].append(task_dict)
            
            cycles_data.append(cycle_dict)
        
        # Import and use the AI recommendation service
        from app.services.ai_recommendation_service import ai_recommendation_service
        
        # Generate real-time recommendations
        recommendations = await ai_recommendation_service.generate_real_time_recommendations(
            client_id=client_id,
            location=location,
            crop_cycles=cycles_data,
            include_weather=include_weather,
            include_market=include_market,
            include_soil=include_soil
        )
        
        # Convert recommendations to response format
        recommendations_response = []
        for rec in recommendations:
            rec_data = {
                "recommendation_id": rec.recommendation_id,
                "title": rec.title,
                "description": rec.description,
                "recommendation_type": rec.recommendation_type.value,
                "priority": rec.priority.value,
                "action_items": rec.action_items,
                "reasoning": rec.reasoning,
                "expected_impact": rec.expected_impact,
                "urgency_hours": rec.urgency_hours,
                "data_sources": rec.data_sources,
                "created_at": rec.created_at.isoformat(),
                "expires_at": rec.expires_at.isoformat() if rec.expires_at else None
            }
            recommendations_response.append(rec_data)
        
        logger.info(f"Generated {len(recommendations_response)} AI recommendations for client {client_id}")
        return recommendations_response
        
    except Exception as e:
        logger.error(f"Error generating AI recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating AI recommendations: {str(e)}")

@router.get("/ai-recommendations/{client_id}", response_model=List[Dict[str, Any]])
async def get_cached_ai_recommendations(
    client_id: str,
    max_recommendations: int = Query(10, description="Maximum number of recommendations to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cached AI recommendations for a client
    
    This endpoint returns previously generated recommendations
    that are still valid and relevant.
    """
    try:
        # Verify user exists
        user = await db.get(User, client_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Import and use the AI recommendation service
        from app.services.ai_recommendation_service import ai_recommendation_service
        
        # Get cached recommendations
        recommendations = await ai_recommendation_service.get_recommendations_for_client(
            client_id, max_recommendations
        )
        
        # Convert to response format
        recommendations_response = []
        for rec in recommendations:
            rec_data = {
                "recommendation_id": rec.recommendation_id,
                "title": rec.title,
                "description": rec.description,
                "recommendation_type": rec.recommendation_type.value,
                "priority": rec.priority.value,
                "action_items": rec.action_items,
                "reasoning": rec.reasoning,
                "expected_impact": rec.expected_impact,
                "urgency_hours": rec.urgency_hours,
                "data_sources": rec.data_sources,
                "created_at": rec.created_at.isoformat(),
                "expires_at": rec.expires_at.isoformat() if rec.expires_at else None
            }
            recommendations_response.append(rec_data)
        
        return recommendations_response
        
    except Exception as e:
        logger.error(f"Error fetching cached AI recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching cached AI recommendations: {str(e)}")
