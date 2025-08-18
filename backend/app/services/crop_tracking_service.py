"""
Crop Tracking Service
Monitors crop progress, manages checklists, and provides tracking insights
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

from app.services.crop_calendar_service import CropCalendar, CropStage
from app.services.weather_tool import WeatherTool
from app.services.real_data_integration_service import RealDataIntegrationService, RealTimeWeatherData
from app.config import settings

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of tracking tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SKIPPED = "skipped"

class ProgressStatus(Enum):
    """Crop progress status"""
    NOT_STARTED = "not_started"
    PLANTED = "planted"
    GERMINATED = "germinated"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURING = "maturing"
    READY_FOR_HARVEST = "ready_for_harvest"
    HARVESTED = "harvested"

@dataclass
class TrackingTask:
    """Individual tracking task"""
    task_id: str
    task_name: str
    task_description: str
    task_type: str  # "observation", "action", "measurement"
    due_date: date
    completed_date: Optional[date] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: str = "medium"  # "low", "medium", "high", "critical"
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    photos: List[str] = None
    location: Optional[Dict[str, float]] = None  # lat, lng

@dataclass
class GrowthObservation:
    """Growth stage observation"""
    observation_id: str
    stage_name: str
    observation_date: date
    growth_percentage: float  # 0.0 to 100.0
    health_score: float  # 0.0 to 10.0
    observations: List[str]
    photos: List[str]
    weather_conditions: Dict[str, Any]
    notes: str
    next_expected_milestone: str
    days_to_next_milestone: int

@dataclass
class CropTracker:
    """Complete crop tracking information"""
    tracker_id: str
    plan_id: str
    farmer_id: str
    crop_name: str
    crop_variety: str
    area_acres: float
    planting_date: date
    expected_harvest_date: date
    
    # Current status
    current_stage: ProgressStatus
    current_stage_name: str
    days_since_planting: int
    days_to_harvest: int
    overall_progress: float  # 0.0 to 100.0
    
    # Tracking data
    tasks: List[TrackingTask]
    observations: List[GrowthObservation]
    crop_calendar: Optional[CropCalendar]
    
    # Weather integration
    weather_alerts: List[str]
    irrigation_recommendations: List[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_observation_date: Optional[date] = None

class CropTrackingService:
    """Service for tracking crop progress and managing tasks"""
    
    def __init__(self):
        self.weather_tool = WeatherTool()
        self.real_data_service = RealDataIntegrationService()
        self.tracker_cache = {}
        self.task_templates = self._initialize_task_templates()
        
        # Initialize LangChain LLM
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.3,  # Lower temperature for more consistent agricultural advice
                max_output_tokens=2048
            )
            self.llm_available = True
            logger.info("LangChain LLM initialized successfully for CropTrackingService")
        except Exception as e:
            logger.warning(f"Failed to initialize LangChain LLM for CropTrackingService: {e}")
            self.llm_available = False
            self.llm = None
        
        # Initialize LangChain prompts
        self._initialize_langchain_prompts()
    
    def _initialize_langchain_prompts(self):
        """Initialize LangChain prompt templates for intelligent task generation"""
        try:
            # Smart checklist generation prompt
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
1. Crop-specific growth requirements and timing
2. Farmer's experience level (beginner/intermediate/expert) - adjust complexity accordingly
3. Farm size and resource availability - scale tasks appropriately
4. Local weather patterns and seasonal factors
5. Soil conditions and improvement needs
6. Market timing and optimization opportunities
7. Risk mitigation and monitoring tasks
8. Local agricultural practices and cultural considerations

Provide your checklist in the following JSON format:
{{
    "tasks": [
        {{
            "task_name": "task name",
            "task_description": "detailed description appropriate for farmer's experience level",
            "task_type": "observation|action|measurement|planning|maintenance",
            "due_date": "YYYY-MM-DD",
            "priority": "critical|high|medium|low",
            "experience_level": "beginner|intermediate|expert",
            "resource_requirements": ["resource 1", "resource 2"],
            "success_criteria": "how to know task is complete",
            "local_tips": ["local tip 1", "local tip 2"],
            "risk_mitigation": "how this task reduces risks",
            "estimated_duration": "estimated time to complete",
            "weather_dependency": "how weather affects this task"
        }}
    ],
    "overall_strategy": "high-level approach to crop management",
    "key_milestones": ["milestone 1", "milestone 2"],
    "success_indicators": ["indicator 1", "indicator 2"],
    "risk_monitoring": ["risk factor 1", "risk factor 2"],
    "local_best_practices": ["local practice 1", "local practice 2"]
}}
""")

            # Task optimization prompt
            self.task_optimization_prompt = ChatPromptTemplate.from_template("""
You are an agricultural efficiency expert optimizing task sequences for Indian farmers.

Current Tasks: {current_tasks}
Crop Stage: {crop_stage}
Weather Forecast: {weather_forecast}
Available Resources: {available_resources}
Farmer Experience: {farmer_experience}

Optimize the task sequence considering:
1. Task dependencies and logical order
2. Weather conditions and optimal timing
3. Resource availability and constraints
4. Farmer's experience and capabilities
5. Risk mitigation and safety
6. Efficiency and time management
7. Local agricultural practices

Provide optimized task sequence in the following JSON format:
{{
    "optimized_sequence": [
        {{
            "task_id": "task_id",
            "optimized_order": 1,
            "reasoning": "why this order is optimal",
            "weather_considerations": "weather factors affecting timing",
            "resource_optimization": "how to optimize resource usage",
            "risk_reduction": "how this order reduces risks"
        }}
    ],
    "efficiency_gains": "estimated time/effort savings",
    "risk_reduction": "overall risk reduction from optimization",
    "resource_optimization": "how resources are better utilized",
    "additional_recommendations": ["recommendation 1", "recommendation 2"]
}}
""")

            logger.info("LangChain prompts initialized successfully for CropTrackingService")
            
        except Exception as e:
            logger.error(f"Error initializing LangChain prompts for CropTrackingService: {e}")
            self.smart_checklist_prompt = None
            self.task_optimization_prompt = None
    
    def _initialize_task_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize task templates for different growth stages"""
        templates = {
            "germination": [
                {
                    "name": "Check Germination Rate",
                    "description": "Count emerged seedlings and calculate germination percentage",
                    "type": "measurement",
                    "priority": "high",
                    "due_days_after_planting": 7
                },
                {
                    "name": "Monitor Soil Moisture",
                    "description": "Ensure soil remains moist but not waterlogged",
                    "type": "observation",
                    "priority": "critical",
                    "due_days_after_planting": 3
                }
            ],
            "vegetative": [
                {
                    "name": "Apply First Fertilizer",
                    "description": "Apply nitrogen-rich fertilizer for vegetative growth",
                    "type": "action",
                    "priority": "high",
                    "due_days_after_planting": 21
                },
                {
                    "name": "Weed Control",
                    "description": "Remove weeds and apply pre-emergence herbicides if needed",
                    "type": "action",
                    "priority": "medium",
                    "due_days_after_planting": 25
                },
                {
                    "name": "Monitor Plant Height",
                    "description": "Measure average plant height and record growth rate",
                    "type": "measurement",
                    "priority": "medium",
                    "due_days_after_planting": 30
                }
            ],
            "flowering": [
                {
                    "name": "Monitor Flower Development",
                    "description": "Check flower formation and pollination status",
                    "type": "observation",
                    "priority": "high",
                    "due_days_after_planting": 56
                },
                {
                    "name": "Pest Monitoring",
                    "description": "Check for common pests during flowering stage",
                    "type": "observation",
                    "priority": "critical",
                    "due_days_after_planting": 58
                }
            ],
            "maturity": [
                {
                    "name": "Assess Maturity",
                    "description": "Check grain/pod maturity indicators",
                    "type": "observation",
                    "priority": "high",
                    "due_days_after_planting": 100
                },
                {
                    "name": "Harvest Planning",
                    "description": "Plan harvest timing and logistics",
                    "type": "action",
                    "priority": "medium",
                    "due_days_after_planting": 105
                }
            ]
        }
        return templates
    
    async def create_crop_tracker(
        self,
        plan_id: str,
        farmer_id: str,
        crop_name: str,
        crop_variety: str,
        area_acres: float,
        planting_date: date,
        crop_calendar: Optional[CropCalendar] = None
    ) -> CropTracker:
        """
        Create a new crop tracker
        
        Args:
            plan_id: Associated crop plan ID
            farmer_id: Farmer's ID
            crop_name: Name of the crop
            crop_variety: Crop variety
            area_acres: Area under cultivation
            planting_date: Date when crop was planted
            crop_calendar: Associated crop calendar
            
        Returns:
            CropTracker object
        """
        try:
            logger.info(f"Creating crop tracker for {crop_name} planted on {planting_date}")
            
            # Calculate expected harvest date
            expected_harvest_date = self._calculate_expected_harvest_date(
                planting_date, crop_calendar
            )
            
            # Generate initial tasks
            initial_tasks = await self._generate_initial_tasks(
                crop_name, planting_date, crop_calendar
            )
            
            # Create tracker
            tracker = CropTracker(
                tracker_id=f"tracker_{farmer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                plan_id=plan_id,
                farmer_id=farmer_id,
                crop_name=crop_name,
                crop_variety=crop_variety,
                area_acres=area_acres,
                planting_date=planting_date,
                expected_harvest_date=expected_harvest_date,
                current_stage=ProgressStatus.PLANTED,
                current_stage_name="Planted",
                days_since_planting=0,
                days_to_harvest=(expected_harvest_date - planting_date).days,
                overall_progress=5.0,  # Initial progress
                tasks=initial_tasks,
                observations=[],
                crop_calendar=crop_calendar,
                weather_alerts=[],
                irrigation_recommendations=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_observation_date=None
            )
            
            # Cache tracker
            self._cache_tracker(tracker.tracker_id, tracker)
            
            logger.info(f"Crop tracker created: {tracker.tracker_id}")
            return tracker
            
        except Exception as e:
            logger.error(f"Error creating crop tracker: {e}")
            raise
    
    def _calculate_expected_harvest_date(
        self, 
        planting_date: date, 
        crop_calendar: Optional[CropCalendar]
    ) -> date:
        """Calculate expected harvest date"""
        try:
            if crop_calendar and crop_calendar.expected_harvest_start:
                return crop_calendar.expected_harvest_start
            
            # Default duration based on crop type
            default_durations = {
                "rice": 120,
                "wheat": 110,
                "maize": 90,
                "cotton": 150,
                "sugarcane": 365
            }
            
            duration_days = default_durations.get(
                crop_calendar.crop_name.lower() if crop_calendar else "rice", 
                120
            )
            
            return planting_date + timedelta(days=duration_days)
            
        except Exception as e:
            logger.error(f"Error calculating harvest date: {e}")
            return planting_date + timedelta(days=120)
    
    async def _generate_initial_tasks(
        self, 
        crop_name: str, 
        planting_date: date, 
        crop_calendar: Optional[CropCalendar]
    ) -> List[TrackingTask]:
        """Generate initial tracking tasks"""
        try:
            tasks = []
            task_id_counter = 1
            
            # Add immediate tasks
            immediate_tasks = [
                {
                    "name": "Confirm Planting",
                    "description": "Verify crop has been planted successfully",
                    "type": "observation",
                    "priority": "critical",
                    "due_days": 0
                },
                {
                    "name": "Check Irrigation System",
                    "description": "Ensure irrigation system is working properly",
                    "type": "action",
                    "priority": "high",
                    "due_days": 1
                }
            ]
            
            for task_data in immediate_tasks:
                task = TrackingTask(
                    task_id=f"task_{task_id_counter:03d}",
                    task_name=task_data["name"],
                    task_description=task_data["description"],
                    task_type=task_data["type"],
                    due_date=planting_date + timedelta(days=task_data["due_days"]),
                    priority=task_data["priority"]
                )
                tasks.append(task)
                task_id_counter += 1
            
            # Add stage-specific tasks from templates
            if crop_calendar:
                for stage in crop_calendar.stages:
                    stage_tasks = self.task_templates.get(stage.stage_name.lower(), [])
                    
                    for task_data in stage_tasks:
                        due_date = planting_date + timedelta(
                            days=task_data["due_days_after_planting"]
                        )
                        
                        task = TrackingTask(
                            task_id=f"task_{task_id_counter:03d}",
                            task_name=task_data["name"],
                            task_description=task_data["description"],
                            task_type=task_data["type"],
                            due_date=due_date,
                            priority=task_data["priority"]
                        )
                        tasks.append(task)
                        task_id_counter += 1
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error generating initial tasks: {e}")
            return []
    
    async def update_crop_progress(
        self, 
        tracker_id: str, 
        new_stage: ProgressStatus,
        observation_notes: Optional[str] = None,
        photos: Optional[List[str]] = None,
        health_score: Optional[float] = None
    ) -> CropTracker:
        """
        Update crop progress to a new stage
        
        Args:
            tracker_id: Tracker ID to update
            new_stage: New progress stage
            observation_notes: Notes about the progress
            photos: Photos documenting the progress
            health_score: Health score (0-10)
            
        Returns:
            Updated CropTracker object
        """
        try:
            tracker = await self.get_tracker(tracker_id)
            if not tracker:
                raise ValueError(f"Tracker not found: {tracker_id}")
            
            # Update current stage
            tracker.current_stage = new_stage
            tracker.current_stage_name = new_stage.value.replace("_", " ").title()
            
            # Calculate progress
            tracker.overall_progress = self._calculate_progress_percentage(
                tracker.current_stage, tracker.crop_calendar
            )
            
            # Create observation
            if observation_notes or photos or health_score is not None:
                observation = GrowthObservation(
                    observation_id=f"obs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    stage_name=tracker.current_stage_name,
                    observation_date=datetime.now().date(),
                    growth_percentage=tracker.overall_progress,
                    health_score=health_score or 8.0,
                    observations=[observation_notes] if observation_notes else [],
                    photos=photos or [],
                    weather_conditions=await self._get_current_weather(tracker),
                    notes=observation_notes or "",
                    next_expected_milestone=self._get_next_milestone(tracker),
                    days_to_next_milestone=self._calculate_days_to_next_milestone(tracker)
                )
                
                tracker.observations.append(observation)
                tracker.last_observation_date = observation.observation_date
            
            # Update days since planting
            tracker.days_since_planting = (datetime.now().date() - tracker.planting_date).days
            tracker.days_to_harvest = max(0, (tracker.expected_harvest_date - datetime.now().date()).days)
            
            # Update weather alerts and recommendations
            tracker.weather_alerts = await self._get_weather_alerts(tracker)
            tracker.irrigation_recommendations = await self._get_irrigation_recommendations(tracker)
            
            # Update timestamp
            tracker.updated_at = datetime.now()
            
            # Update cache
            self._cache_tracker(tracker_id, tracker)
            
            logger.info(f"Updated crop progress for {tracker_id} to {new_stage.value}")
            return tracker
            
        except Exception as e:
            logger.error(f"Error updating crop progress: {e}")
            raise
    
    def _calculate_progress_percentage(
        self, 
        current_stage: ProgressStatus, 
        crop_calendar: Optional[CropCalendar]
    ) -> float:
        """Calculate overall progress percentage"""
        try:
            # Stage progress mapping
            stage_progress = {
                ProgressStatus.NOT_STARTED: 0.0,
                ProgressStatus.PLANTED: 5.0,
                ProgressStatus.GERMINATED: 15.0,
                ProgressStatus.VEGETATIVE: 35.0,
                ProgressStatus.FLOWERING: 60.0,
                ProgressStatus.FRUITING: 75.0,
                ProgressStatus.MATURING: 90.0,
                ProgressStatus.READY_FOR_HARVEST: 95.0,
                ProgressStatus.HARVESTED: 100.0
            }
            
            base_progress = stage_progress.get(current_stage, 0.0)
            
            # Adjust based on crop calendar if available
            if crop_calendar:
                # Add some variation based on calendar
                calendar_adjustment = min(10.0, len(crop_calendar.stages) * 2.0)
                base_progress += calendar_adjustment
            
            return min(100.0, max(0.0, base_progress))
            
        except Exception as e:
            logger.error(f"Error calculating progress percentage: {e}")
            return 0.0
    
    def _get_next_milestone(self, tracker: CropTracker) -> str:
        """Get next expected milestone"""
        try:
            current_stage = tracker.current_stage
            
            milestone_sequence = [
                ProgressStatus.PLANTED,
                ProgressStatus.GERMINATED,
                ProgressStatus.VEGETATIVE,
                ProgressStatus.FLOWERING,
                ProgressStatus.FRUITING,
                ProgressStatus.MATURING,
                ProgressStatus.READY_FOR_HARVEST,
                ProgressStatus.HARVESTED
            ]
            
            try:
                current_index = milestone_sequence.index(current_stage)
                if current_index + 1 < len(milestone_sequence):
                    next_stage = milestone_sequence[current_index + 1]
                    return next_stage.value.replace("_", " ").title()
            except ValueError:
                pass
            
            return "Harvest"
            
        except Exception as e:
            logger.error(f"Error getting next milestone: {e}")
            return "Next Stage"
    
    def _calculate_days_to_next_milestone(self, tracker: CropTracker) -> int:
        """Calculate days to next milestone"""
        try:
            if tracker.crop_calendar:
                # Use crop calendar stages
                current_stage_name = tracker.current_stage_name.lower()
                
                for stage in tracker.crop_calendar.stages:
                    if stage.stage_name.lower() == current_stage_name:
                        # Estimate days to next stage
                        return stage.duration_days
            
            # Default estimates
            default_durations = {
                ProgressStatus.PLANTED: 7,
                ProgressStatus.GERMINATED: 21,
                ProgressStatus.VEGETATIVE: 35,
                ProgressStatus.FLOWERING: 21,
                ProgressStatus.FRUITING: 28,
                ProgressStatus.MATURING: 21,
                ProgressStatus.READY_FOR_HARVEST: 7
            }
            
            return default_durations.get(tracker.current_stage, 14)
            
        except Exception as e:
            logger.error(f"Error calculating days to next milestone: {e}")
            return 14
    
    async def _get_current_weather(self, tracker: CropTracker) -> Dict[str, Any]:
        """Get current weather conditions using real weather data"""
        try:
            # Get real-time weather data if location is available
            if tracker.location and tracker.location.get('lat') and tracker.location.get('lng'):
                try:
                    weather_data = await self.real_data_service.get_real_time_weather(
                        tracker.location['lat'], 
                        tracker.location['lng']
                    )
                    
                    return {
                        "temperature": weather_data.temperature,
                        "humidity": weather_data.humidity,
                        "rainfall": weather_data.rainfall,
                        "wind_speed": weather_data.wind_speed,
                        "description": weather_data.weather_description,
                        "timestamp": weather_data.timestamp.isoformat(),
                        "source": "OpenMeteo API"
                    }
                except Exception as e:
                    logger.warning(f"Failed to fetch real weather data: {e}")
            
            # Fallback to weather tool if real data service fails
            try:
                if tracker.location and tracker.location.get('lat') and tracker.location.get('lng'):
                    weather_result = await self.weather_tool.get_current_weather(
                        tracker.location['lat'], 
                        tracker.location['lng']
                    )
                    
                    if weather_result["status"] == "success":
                        weather_data = weather_result["data"]
                        return {
                            "temperature": weather_data.get("temperature_celsius", 28.0),
                            "humidity": weather_data.get("humidity_percent", 65.0),
                            "rainfall": weather_data.get("precipitation_mm", 0.0),
                            "wind_speed": weather_data.get("wind_speed_kmh", 5.0),
                            "description": weather_data.get("weather_condition", "Partly cloudy"),
                            "source": "Weather Tool"
                        }
            except Exception as e:
                logger.warning(f"Failed to fetch weather from weather tool: {e}")
            
            # Final fallback to placeholder data
            return {
                "temperature": 28.0,
                "humidity": 65.0,
                "rainfall": 0.0,
                "wind_speed": 5.0,
                "description": "Partly cloudy",
                "source": "Fallback data"
            }
            
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return {}
    
    async def _get_weather_alerts(self, tracker: CropTracker) -> List[str]:
        """Get weather alerts for the crop"""
        try:
            alerts = []
            
            # This would integrate with your weather service
            # For now, return placeholder alerts
            if tracker.current_stage in [ProgressStatus.GERMINATED, ProgressStatus.VEGETATIVE]:
                alerts.append("Monitor for drought conditions")
            
            if tracker.current_stage == ProgressStatus.FLOWERING:
                alerts.append("Protect flowers from heavy rainfall")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting weather alerts: {e}")
            return []
    
    async def _get_irrigation_recommendations(self, tracker: CropTracker) -> List[str]:
        """Get irrigation recommendations"""
        try:
            recommendations = []
            
            # Stage-specific irrigation advice
            if tracker.current_stage == ProgressStatus.GERMINATED:
                recommendations.append("Maintain consistent soil moisture")
                recommendations.append("Avoid waterlogging")
            
            elif tracker.current_stage == ProgressStatus.VEGETATIVE:
                recommendations.append("Increase irrigation frequency")
                recommendations.append("Monitor soil moisture at 15cm depth")
            
            elif tracker.current_stage == ProgressStatus.FLOWERING:
                recommendations.append("Ensure adequate water during flowering")
                recommendations.append("Avoid water stress")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting irrigation recommendations: {e}")
            return []
    
    async def get_tracker(self, tracker_id: str) -> Optional[CropTracker]:
        """Get a crop tracker by ID"""
        try:
            # Check cache first
            if tracker_id in self.tracker_cache:
                return self.tracker_cache[tracker_id]
            
            # In a real implementation, this would fetch from database
            return None
            
        except Exception as e:
            logger.error(f"Error getting tracker: {e}")
            return None
    
    async def get_farmer_trackers(self, farmer_id: str) -> List[CropTracker]:
        """Get all trackers for a farmer"""
        try:
            # Filter cached trackers by farmer ID
            farmer_trackers = [
                tracker for tracker in self.tracker_cache.values()
                if tracker.farmer_id == farmer_id
            ]
            
            return farmer_trackers
            
        except Exception as e:
            logger.error(f"Error getting farmer trackers: {e}")
            return []
    
    async def update_task_status(
        self, 
        tracker_id: str, 
        task_id: str, 
        new_status: TaskStatus,
        completion_notes: Optional[str] = None
    ) -> bool:
        """Update task status"""
        try:
            tracker = await self.get_tracker(tracker_id)
            if not tracker:
                return False
            
            # Find and update task
            for task in tracker.tasks:
                if task.task_id == task_id:
                    task.status = new_status
                    if new_status == TaskStatus.COMPLETED:
                        task.completed_date = datetime.now().date()
                    if completion_notes:
                        task.notes = completion_notes
                    
                    # Update tracker
                    tracker.updated_at = datetime.now()
                    self._cache_tracker(tracker_id, tracker)
                    
                    logger.info(f"Updated task {task_id} status to {new_status.value}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    async def add_custom_task(
        self, 
        tracker_id: str, 
        task_name: str, 
        task_description: str,
        due_date: date,
        priority: str = "medium"
    ) -> Optional[TrackingTask]:
        """Add a custom task to the tracker"""
        try:
            tracker = await self.get_tracker(tracker_id)
            if not tracker:
                return None
            
            # Create new task
            new_task = TrackingTask(
                task_id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                task_name=task_name,
                task_description=task_description,
                task_type="custom",
                due_date=due_date,
                priority=priority
            )
            
            # Add to tracker
            tracker.tasks.append(new_task)
            tracker.updated_at = datetime.now()
            
            # Update cache
            self._cache_tracker(tracker_id, tracker)
            
            logger.info(f"Added custom task to tracker {tracker_id}")
            return new_task
            
        except Exception as e:
            logger.error(f"Error adding custom task: {e}")
            return None
    
    async def generate_smart_checklist(
        self,
        crop_name: str,
        crop_variety: str,
        planting_date: date,
        farmer_profile: Dict[str, Any],
        weather_forecast: Optional[Dict[str, Any]] = None,
        soil_conditions: Optional[Dict[str, Any]] = None,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> List[TrackingTask]:
        """
        Generate smart, personalized checklist based on multiple factors using LangChain LLM
        """
        try:
            logger.info(f"Generating smart checklist for {crop_name} ({crop_variety})")
            
            # Use LangChain LLM for enhanced checklist generation if available
            if self.llm_available and self.smart_checklist_prompt:
                try:
                    # Prepare context for LLM
                    llm_context = await self._prepare_llm_context_for_checklist(
                        crop_name, crop_variety, planting_date, farmer_profile, 
                        weather_forecast, soil_conditions, market_conditions
                    )
                    
                    # Generate LLM-enhanced checklist
                    llm_checklist = await self._generate_llm_checklist(llm_context)
                    
                    if llm_checklist:
                        # Convert LLM response to TrackingTask objects
                        smart_tasks = await self._convert_llm_checklist_to_tasks(llm_checklist, planting_date)
                        
                        # Sort by priority and due date
                        smart_tasks.sort(key=lambda x: (self._get_priority_score(x.priority), x.due_date))
                        
                        logger.info(f"Generated {len(smart_tasks)} LLM-enhanced smart tasks for {crop_name}")
                        return smart_tasks
                        
                except Exception as e:
                    logger.warning(f"LLM checklist generation failed, falling back to rule-based: {e}")
            
            # Fallback to rule-based checklist generation
            return await self._generate_rule_based_checklist(
                crop_name, crop_variety, planting_date, farmer_profile, 
                weather_forecast, soil_conditions, market_conditions
            )
            
        except Exception as e:
            logger.error(f"Error generating smart checklist: {e}")
            # Fallback to basic tasks
            return await self._generate_initial_tasks(crop_name, planting_date, None)
    
    async def _enhance_tasks_with_ai(
        self,
        base_tasks: List[TrackingTask],
        crop_name: str,
        crop_variety: str,
        farmer_profile: Dict[str, Any]
    ) -> List[TrackingTask]:
        """Enhance base tasks with AI-powered recommendations"""
        try:
            enhanced_tasks = base_tasks.copy()
            
            # Add crop-specific tasks based on variety
            variety_tasks = await self._get_variety_specific_tasks(crop_name, crop_variety)
            enhanced_tasks.extend(variety_tasks)
            
            # Add experience-based tasks
            experience_tasks = await self._get_experience_based_tasks(
                farmer_profile.get("experience_years", 0)
            )
            enhanced_tasks.extend(experience_tasks)
            
            # Add farm size-based tasks
            size_tasks = await self._get_farm_size_tasks(
                farmer_profile.get("farm_size", 1.0)
            )
            enhanced_tasks.extend(size_tasks)
            
            # Add irrigation-specific tasks
            irrigation_tasks = await self._get_irrigation_tasks(
                farmer_profile.get("irrigation_type", "rainfed")
            )
            enhanced_tasks.extend(irrigation_tasks)
            
            return enhanced_tasks
            
        except Exception as e:
            logger.error(f"Error enhancing tasks with AI: {e}")
            return base_tasks
    
    async def _adjust_tasks_for_weather(
        self,
        tasks: List[TrackingTask],
        weather_forecast: Dict[str, Any],
        planting_date: date
    ) -> List[TrackingTask]:
        """Adjust task timing and priority based on weather forecast"""
        try:
            adjusted_tasks = []
            
            for task in tasks:
                adjusted_task = task
                
                # Check if weather affects this task
                weather_impact = await self._assess_weather_impact(task, weather_forecast)
                
                if weather_impact["should_adjust"]:
                    # Adjust due date based on weather
                    optimal_date = await self._find_optimal_weather_date(
                        task, weather_forecast, planting_date
                    )
                    if optimal_date:
                        adjusted_task.due_date = optimal_date
                    
                    # Adjust priority based on weather urgency
                    if weather_impact["urgency"] == "high":
                        adjusted_task.priority = "critical"
                    elif weather_impact["urgency"] == "medium":
                        adjusted_task.priority = "high"
                    
                    # Add weather-specific notes
                    if weather_impact["notes"]:
                        adjusted_task.notes = (adjusted_task.notes or "") + f" | Weather: {weather_impact['notes']}"
                
                adjusted_tasks.append(adjusted_task)
            
            return adjusted_tasks
            
        except Exception as e:
            logger.error(f"Error adjusting tasks for weather: {e}")
            return tasks
    
    async def _customize_tasks_for_soil(
        self,
        tasks: List[TrackingTask],
        soil_conditions: Dict[str, Any],
        crop_name: str
    ) -> List[TrackingTask]:
        """Customize tasks based on soil conditions"""
        try:
            customized_tasks = tasks.copy()
            
            # Add soil-specific tasks
            soil_tasks = await self._get_soil_based_tasks(soil_conditions, crop_name)
            customized_tasks.extend(soil_tasks)
            
            # Modify existing tasks based on soil conditions
            for task in customized_tasks:
                if "fertilizer" in task.task_name.lower():
                    task = await self._customize_fertilizer_task(task, soil_conditions)
                elif "irrigation" in task.task_name.lower():
                    task = await self._customize_irrigation_task(task, soil_conditions)
            
            return customized_tasks
            
        except Exception as e:
            logger.error(f"Error customizing tasks for soil: {e}")
            return tasks
    
    async def _optimize_tasks_for_market(
        self,
        tasks: List[TrackingTask],
        market_conditions: Dict[str, Any],
        crop_name: str
    ) -> List[TrackingTask]:
        """Optimize tasks based on market conditions"""
        try:
            optimized_tasks = tasks.copy()
            
            # Add market-timing tasks
            market_tasks = await self._get_market_timing_tasks(market_conditions, crop_name)
            optimized_tasks.extend(market_tasks)
            
            # Adjust harvest-related task priorities
            for task in optimized_tasks:
                if "harvest" in task.task_name.lower():
                    task = await self._optimize_harvest_task(task, market_conditions)
            
            return optimized_tasks
            
        except Exception as e:
            logger.error(f"Error optimizing tasks for market: {e}")
            return tasks
    
    async def _personalize_tasks_for_farmer(
        self,
        tasks: List[TrackingTask],
        farmer_profile: Dict[str, Any]
    ) -> List[TrackingTask]:
        """Personalize tasks based on farmer's profile and preferences"""
        try:
            personalized_tasks = tasks.copy()
            
            # Adjust task complexity based on experience
            experience_years = farmer_profile.get("experience_years", 0)
            for task in personalized_tasks:
                if experience_years < 2:
                    # Add more detailed descriptions for beginners
                    task.task_description += " (Beginner-friendly: Take photos and ask for help if unsure)"
                elif experience_years > 10:
                    # Simplify descriptions for experts
                    task.task_description = task.task_description.split(" (")[0]
            
            # Add language-specific notes
            language = farmer_profile.get("language", "en")
            if language in ["hi", "kn"]:
                for task in personalized_tasks:
                    task.notes = (task.notes or "") + f" | Language: {language}"
            
            # Add location-specific context
            if farmer_profile.get("pincode"):
                for task in personalized_tasks:
                    task.notes = (task.notes or "") + f" | Location: {farmer_profile['pincode']}"
            
            return personalized_tasks
            
        except Exception as e:
            logger.error(f"Error personalizing tasks for farmer: {e}")
            return tasks
    
    def _get_priority_score(self, priority: str) -> int:
        """Get numeric score for priority sorting"""
        priority_scores = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        return priority_scores.get(priority, 3)
    
    async def _get_variety_specific_tasks(
        self, 
        crop_name: str, 
        crop_variety: str
    ) -> List[TrackingTask]:
        """Get tasks specific to crop variety"""
        try:
            # This would typically integrate with crop database
            # For now, return variety-specific examples
            variety_tasks = []
            
            if "hybrid" in crop_variety.lower():
                variety_tasks.append(TrackingTask(
                    task_id=f"variety_task_{len(variety_tasks):03d}",
                    task_name="Monitor Hybrid Vigor",
                    task_description="Check for enhanced growth characteristics specific to hybrid variety",
                    task_type="observation",
                    due_date=date.today() + timedelta(days=14),
                    priority="medium"
                ))
            
            if "drought_resistant" in crop_variety.lower():
                variety_tasks.append(TrackingTask(
                    task_id=f"variety_task_{len(variety_tasks):03d}",
                    task_name="Drought Stress Monitoring",
                    task_description="Monitor crop response to water stress conditions",
                    task_type="observation",
                    due_date=date.today() + timedelta(days=21),
                    priority="high"
                ))
            
            return variety_tasks
            
        except Exception as e:
            logger.error(f"Error getting variety-specific tasks: {e}")
            return []
    
    async def _get_experience_based_tasks(self, experience_years: int) -> List[TrackingTask]:
        """Get tasks based on farmer's experience level"""
        try:
            experience_tasks = []
            
            if experience_years < 2:
                # Beginner tasks
                experience_tasks.append(TrackingTask(
                    task_id=f"exp_task_{len(experience_tasks):03d}",
                    task_name="Learning Documentation",
                    task_description="Take photos and notes to learn from this growing season",
                    task_type="observation",
                    due_date=date.today() + timedelta(days=7),
                    priority="medium"
                ))
            
            elif experience_years > 10:
                # Expert tasks
                experience_tasks.append(TrackingTask(
                    task_id=f"exp_task_{len(experience_tasks):03d}",
                    task_name="Advanced Optimization",
                    task_description="Fine-tune practices based on your extensive experience",
                    task_type="action",
                    due_date=date.today() + timedelta(days=10),
                    priority="medium"
                ))
            
            return experience_tasks
            
        except Exception as e:
            logger.error(f"Error getting experience-based tasks: {e}")
            return []
    
    async def _get_farm_size_tasks(self, farm_size: float) -> List[TrackingTask]:
        """Get tasks based on farm size"""
        try:
            size_tasks = []
            
            if farm_size > 10:
                # Large farm tasks
                size_tasks.append(TrackingTask(
                    task_id=f"size_task_{len(size_tasks):03d}",
                    task_name="Efficiency Planning",
                    task_description="Plan labor and equipment allocation for large area",
                    task_type="action",
                    due_date=date.today() + timedelta(days=5),
                    priority="high"
                ))
            
            elif farm_size < 2:
                # Small farm tasks
                size_tasks.append(TrackingTask(
                    task_id=f"size_task_{len(size_tasks):03d}",
                    task_name="Intensive Management",
                    task_description="Focus on maximizing yield from small area",
                    task_type="planning",
                    due_date=date.today() + timedelta(days=3),
                    priority="medium"
                ))
            
            return size_tasks
            
        except Exception as e:
            logger.error(f"Error getting farm size tasks: {e}")
            return []
    
    async def _get_irrigation_tasks(self, irrigation_type: str) -> List[TrackingTask]:
        """Get tasks based on irrigation type"""
        try:
            irrigation_tasks = []
            
            if irrigation_type == "drip":
                irrigation_tasks.append(TrackingTask(
                    task_id=f"irr_task_{len(irrigation_tasks):03d}",
                    task_name="Drip System Maintenance",
                    task_description="Check for clogged emitters and system pressure",
                    task_type="maintenance",
                    due_date=date.today() + timedelta(days=2),
                    priority="high"
                ))
            
            elif irrigation_type == "sprinkler":
                irrigation_tasks.append(TrackingTask(
                    task_id=f"irr_task_{len(irrigation_tasks):03d}",
                    task_name="Sprinkler Coverage Check",
                    task_description="Verify uniform water distribution across field",
                    task_type="observation",
                    due_date=date.today() + timedelta(days=3),
                    priority="medium"
                ))
            
            elif irrigation_type == "rainfed":
                irrigation_tasks.append(TrackingTask(
                    task_id=f"irr_task_{len(irrigation_tasks):03d}",
                    task_name="Rainfall Monitoring",
                    task_description="Track rainfall and adjust practices accordingly",
                    task_type="observation",
                    due_date=date.today() + timedelta(days=1),
                    priority="critical"
                ))
            
            return irrigation_tasks
            
        except Exception as e:
            logger.error(f"Error getting irrigation tasks: {e}")
            return []
    
    async def _assess_weather_impact(
        self, 
        task: TrackingTask, 
        weather_forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess how weather affects a specific task"""
        try:
            # This would integrate with weather service
            # For now, return basic assessment
            return {
                "should_adjust": False,
                "urgency": "low",
                "notes": "Weather conditions suitable for task"
            }
        except Exception as e:
            logger.error(f"Error assessing weather impact: {e}")
            return {"should_adjust": False, "urgency": "low", "notes": ""}
    
    async def _find_optimal_weather_date(
        self, 
        task: TrackingTask, 
        weather_forecast: Dict[str, Any], 
        planting_date: date
    ) -> Optional[date]:
        """Find optimal date for task based on weather"""
        try:
            # This would analyze weather forecast for optimal conditions
            # For now, return None (no adjustment)
            return None
        except Exception as e:
            logger.error(f"Error finding optimal weather date: {e}")
            return None
    
    async def _get_soil_based_tasks(
        self, 
        soil_conditions: Dict[str, Any], 
        crop_name: str
    ) -> List[TrackingTask]:
        """Get tasks based on soil conditions"""
        try:
            soil_tasks = []
            
            # Add soil-specific tasks based on conditions
            if soil_conditions.get("ph_level"):
                ph_level = soil_conditions["ph_level"]
                if ph_level < 6.0:
                    soil_tasks.append(TrackingTask(
                        task_id=f"soil_task_{len(soil_tasks):03d}",
                        task_name="Lime Application",
                        task_description=f"Apply lime to raise soil pH from {ph_level} to optimal range",
                        task_type="action",
                        due_date=date.today() + timedelta(days=5),
                        priority="high"
                    ))
                elif ph_level > 8.0:
                    soil_tasks.append(TrackingTask(
                        task_id=f"soil_task_{len(soil_tasks):03d}",
                        task_name="Sulfur Application",
                        task_description=f"Apply sulfur to lower soil pH from {ph_level} to optimal range",
                        task_type="action",
                        due_date=date.today() + timedelta(days=5),
                        priority="high"
                    ))
            
            if soil_conditions.get("organic_matter"):
                om_level = soil_conditions["organic_matter"]
                if om_level < 2.0:
                    soil_tasks.append(TrackingTask(
                        task_id=f"soil_task_{len(soil_tasks):03d}",
                        task_name="Organic Matter Improvement",
                        task_description="Add compost or manure to improve soil organic matter",
                        task_type="action",
                        due_date=date.today() + timedelta(days=7),
                        priority="medium"
                    ))
            
            return soil_tasks
            
        except Exception as e:
            logger.error(f"Error getting soil-based tasks: {e}")
            return []
    
    async def _customize_fertilizer_task(
        self, 
        task: TrackingTask, 
        soil_conditions: Dict[str, Any]
    ) -> TrackingTask:
        """Customize fertilizer task based on soil conditions"""
        try:
            customized_task = task
            
            # Add soil-specific fertilizer recommendations
            if soil_conditions.get("nitrogen_n"):
                n_level = soil_conditions["nitrogen_n"]
                if n_level < 50:
                    customized_task.task_description += f" (High N fertilizer recommended - current level: {n_level} kg/ha)"
                elif n_level > 150:
                    customized_task.task_description += f" (Low N fertilizer recommended - current level: {n_level} kg/ha)"
            
            if soil_conditions.get("phosphorus_p"):
                p_level = soil_conditions["phosphorus_p"]
                if p_level < 20:
                    customized_task.task_description += f" (Phosphorus application needed - current level: {p_level} kg/ha)"
            
            return customized_task
            
        except Exception as e:
            logger.error(f"Error customizing fertilizer task: {e}")
            return task
    
    async def _customize_irrigation_task(
        self, 
        task: TrackingTask, 
        soil_conditions: Dict[str, Any]
    ) -> TrackingTask:
        """Customize irrigation task based on soil conditions"""
        try:
            customized_task = task
            
            # Add soil-specific irrigation recommendations
            if soil_conditions.get("soil_type"):
                soil_type = soil_conditions["soil_type"]
                if soil_type == "sandy":
                    customized_task.task_description += " (Frequent light irrigation - sandy soil drains quickly)"
                elif soil_type == "clay":
                    customized_task.task_description += " (Less frequent heavy irrigation - clay soil retains water)"
            
            if soil_conditions.get("water_holding_capacity"):
                whc = soil_conditions["water_holding_capacity"]
                if whc < 100:
                    customized_task.task_description += f" (Low water holding capacity: {whc} mm - monitor closely)"
                elif whc > 200:
                    customized_task.task_description += f" (High water holding capacity: {whc} mm - less frequent irrigation)"
            
            return customized_task
            
        except Exception as e:
            logger.error(f"Error customizing irrigation task: {e}")
            return task
    
    async def _get_market_timing_tasks(
        self, 
        market_conditions: Dict[str, Any], 
        crop_name: str
    ) -> List[TrackingTask]:
        """Get market timing tasks based on market conditions"""
        try:
            market_tasks = []
            
            # Add market-timing tasks
            if market_conditions.get("price_trend"):
                price_trend = market_conditions["price_trend"]
                if price_trend == "rising":
                    market_tasks.append(TrackingTask(
                        task_id=f"market_task_{len(market_tasks):03d}",
                        task_name="Harvest Timing Optimization",
                        task_description="Consider delaying harvest to benefit from rising prices",
                        task_type="planning",
                        due_date=date.today() + timedelta(days=14),
                        priority="medium"
                    ))
                elif price_trend == "falling":
                    market_tasks.append(TrackingTask(
                        task_id=f"market_task_{len(market_tasks):03d}",
                        task_name="Early Harvest Planning",
                        task_description="Consider early harvest to avoid further price drops",
                        task_type="planning",
                        due_date=date.today() + timedelta(days=7),
                        priority="high"
                    ))
            
            if market_conditions.get("demand_forecast"):
                demand = market_conditions["demand_forecast"]
                if demand == "high":
                    market_tasks.append(TrackingTask(
                        task_id=f"market_task_{len(market_tasks):03d}",
                        task_name="Quality Focus",
                        task_description="Focus on quality to meet high demand expectations",
                        task_type="action",
                        due_date=date.today() + timedelta(days=5),
                        priority="medium"
                    ))
            
            return market_tasks
            
        except Exception as e:
            logger.error(f"Error getting market timing tasks: {e}")
            return []
    
    async def _optimize_harvest_task(
        self, 
        task: TrackingTask, 
        market_conditions: Dict[str, Any]
    ) -> TrackingTask:
        """Optimize harvest task based on market conditions"""
        try:
            optimized_task = task
            
            # Adjust harvest task based on market conditions
            if market_conditions.get("price_trend") == "rising":
                optimized_task.priority = "high"
                optimized_task.task_description += " (Market prices rising - optimize harvest timing)"
            elif market_conditions.get("price_trend") == "falling":
                optimized_task.priority = "critical"
                optimized_task.task_description += " (Market prices falling - harvest soon to minimize losses)"
            
            if market_conditions.get("storage_availability"):
                storage = market_conditions["storage_availability"]
                if storage == "limited":
                    optimized_task.task_description += " (Limited storage - plan immediate sale)"
                elif storage == "available":
                    optimized_task.task_description += " (Storage available - can hold for better prices)"
            
            return optimized_task
            
        except Exception as e:
            logger.error(f"Error optimizing harvest task: {e}")
            return task
    
    def _cache_tracker(self, tracker_id: str, tracker: CropTracker):
        """Cache a crop tracker"""
        try:
            self.tracker_cache[tracker_id] = tracker
            
            # Limit cache size
            if len(self.tracker_cache) > 100:
                # Remove oldest entries
                oldest_id = min(self.tracker_cache.keys())
                del self.tracker_cache[oldest_id]
                
        except Exception as e:
            logger.error(f"Error caching tracker: {e}")
    
    def export_tracker_to_json(self, tracker: CropTracker, filename: str) -> bool:
        """Export tracker data to JSON file"""
        try:
            # Convert tracker to JSON-serializable format
            tracker_data = {
                "tracker_id": tracker.tracker_id,
                "plan_id": tracker.plan_id,
                "farmer_id": tracker.farmer_id,
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
                        "status": task.status.value,
                        "due_date": task.due_date.isoformat(),
                        "completed_date": task.completed_date.isoformat() if task.completed_date else None,
                        "priority": task.priority
                    } for task in tracker.tasks
                ],
                "observations": [
                    {
                        "stage_name": obs.stage_name,
                        "observation_date": obs.observation_date.isoformat(),
                        "growth_percentage": obs.growth_percentage,
                        "health_score": obs.health_score,
                        "notes": obs.notes
                    } for obs in tracker.observations
                ],
                "weather_alerts": tracker.weather_alerts,
                "irrigation_recommendations": tracker.irrigation_recommendations,
                "created_at": tracker.created_at.isoformat(),
                "updated_at": tracker.updated_at.isoformat()
            }
            
            # Write to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported tracker to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting tracker: {e}")
            return False

    async def _prepare_llm_context_for_checklist(
        self,
        crop_name: str,
        crop_variety: str,
        planting_date: date,
        farmer_profile: Dict[str, Any],
        weather_forecast: Optional[Dict[str, Any]] = None,
        soil_conditions: Optional[Dict[str, Any]] = None,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare context for LLM-based checklist generation"""
        try:
            # Convert planting_date to string if it's a date object
            if isinstance(planting_date, str):
                planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d").date()
            else:
                planting_date_obj = planting_date
                
            context = {
                "crop_name": crop_name,
                "crop_variety": crop_variety,
                "planting_date": planting_date_obj.isoformat(),
                "days_since_planting": (datetime.now().date() - planting_date_obj).days,
                "farmer_profile": {
                    "experience_years": farmer_profile.get("experience_years", 0),
                    "farm_size": farmer_profile.get("farm_size", 1.0),
                    "irrigation_type": farmer_profile.get("irrigation_type", "rainfed"),
                    "location": farmer_profile.get("location", {}),
                }
            }
            
            if weather_forecast:
                context["weather_forecast"] = weather_forecast
                
            if soil_conditions:
                context["soil_conditions"] = soil_conditions
                
            if market_conditions:
                context["market_conditions"] = market_conditions
                
            return context
            
        except Exception as e:
            logger.error(f"Error preparing LLM context: {e}")
            return {}

    async def _generate_llm_checklist(self, context: Dict[str, Any]) -> Optional[str]:
        """Generate checklist using LLM"""
        try:
            if not self.llm_available or not self.smart_checklist_prompt:
                return None
                
            # Get farmer profile from context
            farmer_profile = context.get("farmer_profile", {})
            
            # Format the prompt with all required parameters
            prompt = self.smart_checklist_prompt.format(
                crop_name=context.get("crop_name", "crop"),
                crop_variety=context.get("crop_variety", "standard"),
                planting_date=context.get("planting_date", ""),
                location=farmer_profile.get("location", {}).get("name", "Karnataka, India"),
                farm_size=farmer_profile.get("farm_size", 1.0),
                experience_years=farmer_profile.get("experience_years", 0),
                irrigation_type=farmer_profile.get("irrigation_type", "rainfed"),
                language="English",
                soil_health_summary="Good soil conditions with balanced nutrients",
                weather_summary="Normal seasonal weather patterns",
                market_summary="Stable market conditions for the crop"
            )
            
            # Generate response using LLM
            response = await self.llm.agenerate([prompt])
            
            if response and response.generations:
                return response.generations[0][0].text
                
            return None
            
        except Exception as e:
            logger.error(f"Error generating LLM checklist: {e}")
            return None

    async def _convert_llm_checklist_to_tasks(
        self,
        llm_response: str,
        planting_date: date
    ) -> List[TrackingTask]:
        """Convert LLM response to TrackingTask objects"""
        try:
            tasks = []
            
            if not llm_response:
                return tasks
                
            # Convert planting_date to date object if it's a string
            if isinstance(planting_date, str):
                planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d").date()
            else:
                planting_date_obj = planting_date
                
            # Simple parsing of LLM response
            lines = llm_response.split('\n')
            task_id_counter = 1
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Try to extract task information
                if ':' in line or '-' in line:
                    # Simple task parsing
                    task_name = line.split(':')[0] if ':' in line else line.split('-')[0]
                    task_name = task_name.strip().strip('*').strip('-').strip()
                    
                    if task_name and len(task_name) > 3:
                        # Create a basic task
                        task = TrackingTask(
                            task_id=f"llm_task_{task_id_counter}",
                            task_name=task_name,
                            task_description=f"AI-generated task: {task_name}",
                            task_type="action",
                            due_date=planting_date_obj + timedelta(days=task_id_counter * 7),  # Spread tasks
                            priority="medium"
                        )
                        tasks.append(task)
                        task_id_counter += 1
                        
            return tasks
            
        except Exception as e:
            logger.error(f"Error converting LLM checklist to tasks: {e}")
            return []

    async def _generate_rule_based_checklist(
        self,
        crop_name: str,
        crop_variety: str,
        planting_date: date,
        farmer_profile: Dict[str, Any],
        weather_forecast: Optional[Dict[str, Any]] = None,
        soil_conditions: Optional[Dict[str, Any]] = None,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> List[TrackingTask]:
        """Generate rule-based checklist as fallback"""
        try:
            logger.info(f"Generating rule-based checklist for {crop_name}")
            
            # Convert planting_date to date object if it's a string
            if isinstance(planting_date, str):
                planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d").date()
            else:
                planting_date_obj = planting_date
            
            # Start with basic tasks
            base_tasks = await self._generate_initial_tasks(crop_name, planting_date_obj, None)
            
            # Enhance with AI-based customization
            enhanced_tasks = await self._enhance_tasks_with_ai(
                base_tasks, crop_name, crop_variety, farmer_profile
            )
            
            # Adjust for weather conditions
            if weather_forecast:
                enhanced_tasks = await self._adjust_tasks_for_weather(
                    enhanced_tasks, weather_forecast, planting_date_obj
                )
            
            # Customize for soil conditions
            if soil_conditions:
                enhanced_tasks = await self._customize_tasks_for_soil(
                    enhanced_tasks, soil_conditions
                )
            
            # Optimize for market conditions
            if market_conditions:
                enhanced_tasks = await self._optimize_tasks_for_market(
                    enhanced_tasks, market_conditions
                )
            
            # Personalize for farmer profile
            enhanced_tasks = await self._personalize_tasks_for_farmer(
                enhanced_tasks, farmer_profile
            )
            
            # Sort by priority and due date
            enhanced_tasks.sort(key=lambda x: (self._get_priority_score(x.priority), x.due_date))
            
            logger.info(f"Generated {len(enhanced_tasks)} rule-based tasks for {crop_name}")
            return enhanced_tasks
            
        except Exception as e:
            logger.error(f"Error generating rule-based checklist: {e}")
            # Fallback to basic tasks
            if isinstance(planting_date, str):
                planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d").date()
            else:
                planting_date_obj = planting_date
            return await self._generate_initial_tasks(crop_name, planting_date_obj, None)

# Example usage and testing
async def test_crop_tracking_service():
    """Test the crop tracking service"""
    service = CropTrackingService()
    
    # Test creating a tracker
    print("Creating crop tracker...")
    planting_date = datetime.now().date()
    
    tracker = await service.create_crop_tracker(
        plan_id="test_plan_001",
        farmer_id="test_farmer_003",
        crop_name="rice",
        crop_variety="IR64",
        area_acres=2.5,
        planting_date=planting_date
    )
    
    print(f"\n✅ Crop tracker created!")
    print(f"Tracker ID: {tracker.tracker_id}")
    print(f"Crop: {tracker.crop_name} ({tracker.crop_variety})")
    print(f"Area: {tracker.area_acres} acres")
    print(f"Planting Date: {tracker.planting_date}")
    print(f"Expected Harvest: {tracker.expected_harvest_date}")
    print(f"Current Stage: {tracker.current_stage.value}")
    print(f"Progress: {tracker.overall_progress:.1f}%")
    
    print(f"\nInitial Tasks ({len(tracker.tasks)}):")
    for task in tracker.tasks[:3]:  # Show first 3 tasks
        print(f"  {task.task_name} - {task.status.value} - Due: {task.due_date}")
    
    # Test progress update
    print(f"\nUpdating progress to germination...")
    updated_tracker = await service.update_crop_progress(
        tracker.tracker_id,
        ProgressStatus.GERMINATED,
        observation_notes="Seeds have germinated successfully",
        health_score=8.5
    )
    
    print(f"Updated Progress: {updated_tracker.overall_progress:.1f}%")
    print(f"Current Stage: {updated_tracker.current_stage_name}")
    print(f"Days Since Planting: {updated_tracker.days_since_planting}")
    
    # Test task completion
    if updated_tracker.tasks:
        first_task = updated_tracker.tasks[0]
        print(f"\nCompleting task: {first_task.task_name}")
        success = await service.update_task_status(
            updated_tracker.tracker_id,
            first_task.task_id,
            TaskStatus.COMPLETED,
            "Planting confirmed, all seeds planted"
        )
        print(f"Task completion: {'✅ Success' if success else '❌ Failed'}")
    
    # Export tracker
    export_success = service.export_tracker_to_json(updated_tracker, "test_crop_tracker.json")
    print(f"\nTracker Export: {'✅ Success' if export_success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_crop_tracking_service())
