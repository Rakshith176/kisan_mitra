"""
Data Collection Coordinator Service
Orchestrates data collection from multiple sources and provides unified access
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
import aiohttp
from dataclasses import dataclass
from app.services.soil_health_service import SoilHealthService, SoilHealthData
from app.services.crop_calendar_service import CropCalendarService, CropCalendar, Season
from app.services.scheme_matching_service import SchemeMatchingService, SchemeMatch
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class DataCollectionResult:
    """Result of data collection operation"""
    source_name: str
    data_type: str
    success: bool
    data_count: int
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    reliability_score: float = 0.0

@dataclass
class UnifiedFarmerData:
    """Unified data structure for farmer information"""
    farmer_id: str
    location: Dict[str, float]  # lat, lng
    pincode: str
    district: str
    state: str
    
    # Soil health data
    soil_health: Optional[SoilHealthData] = None
    
    # Crop calendar data
    crop_calendars: List[CropCalendar] = None
    
    # Government schemes
    eligible_schemes: List[SchemeMatch] = None
    
    # Data freshness
    last_updated: datetime = None
    data_reliability_score: float = 0.0

class DataCollectionCoordinator:
    """Coordinates data collection from multiple sources"""
    
    def __init__(self):
        self.soil_service = SoilHealthService()
        self.crop_calendar_service = CropCalendarService()
        self.scheme_service = SchemeMatchingService()
        self.cache_duration_hours = 24
        self.session = None
        
        # Data cache
        self.data_cache = {}
        self.cache_timestamps = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def collect_comprehensive_farmer_data(
        self, 
        farmer_profile: Dict[str, Any],
        force_refresh: bool = False
    ) -> UnifiedFarmerData:
        """
        Collect comprehensive data for a farmer from all sources
        
        Args:
            farmer_profile: Farmer's profile information
            force_refresh: Force refresh of cached data
            
        Returns:
            UnifiedFarmerData object with all collected information
        """
        try:
            start_time = datetime.now()
            farmer_id = farmer_profile.get("client_id", "unknown")
            
            logger.info(f"Starting comprehensive data collection for farmer {farmer_id}")
            
            # Check cache first
            if not force_refresh and self._is_cache_valid(farmer_id):
                cached_data = self.data_cache.get(farmer_id)
                if cached_data:
                    logger.info(f"Returning cached data for farmer {farmer_id}")
                    return cached_data
            
            # Collect data from all sources
            collection_results = await self._collect_all_data_sources(farmer_profile)
            
            # Create unified data structure
            unified_data = await self._create_unified_data(farmer_profile, collection_results)
            
            # Cache the results
            self._cache_data(farmer_id, unified_data)
            
            # Log collection summary
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Data collection completed for farmer {farmer_id} in {execution_time:.2f}ms")
            
            return unified_data
            
        except Exception as e:
            logger.error(f"Error in comprehensive data collection: {e}")
            # Return partial data if available
            return await self._create_partial_data(farmer_profile)
    
    async def _collect_all_data_sources(self, farmer_profile: Dict[str, Any]) -> Dict[str, DataCollectionResult]:
        """Collect data from all available sources"""
        try:
            collection_results = {}
            
            # Collect soil health data
            soil_result = await self._collect_soil_health_data(farmer_profile)
            collection_results["soil_health"] = soil_result
            
            # Collect crop calendar data
            calendar_result = await self._collect_crop_calendar_data(farmer_profile)
            collection_results["crop_calendar"] = calendar_result
            
            # Collect government scheme data
            scheme_result = await self._collect_scheme_data(farmer_profile)
            collection_results["government_schemes"] = scheme_result
            
            return collection_results
            
        except Exception as e:
            logger.error(f"Error collecting data from all sources: {e}")
            return {}
    
    async def _collect_soil_health_data(self, farmer_profile: Dict[str, Any]) -> DataCollectionResult:
        """Collect soil health data"""
        try:
            start_time = datetime.now()
            
            # Get location information
            pincode = farmer_profile.get("pincode")
            lat = farmer_profile.get("lat")
            lng = farmer_profile.get("lon")
            
            if not pincode and (not lat or not lng):
                return DataCollectionResult(
                    source_name="Soil Health Service",
                    data_type="soil_health",
                    success=False,
                    data_count=0,
                    error_message="No location information available",
                    execution_time_ms=0.0,
                    reliability_score=0.0
                )
            
            # Collect soil data
            if pincode:
                soil_data = await self.soil_service.get_soil_data_by_pincode(pincode)
            else:
                # Use lat/lng if available
                soil_data = None  # Would need to implement lat/lng based search
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if soil_data:
                return DataCollectionResult(
                    source_name="Soil Health Service",
                    data_type="soil_health",
                    success=True,
                    data_count=1,
                    execution_time_ms=execution_time,
                    reliability_score=soil_data.reliability_score
                )
            else:
                return DataCollectionResult(
                    source_name="Soil Health Service",
                    data_type="soil_health",
                    success=False,
                    data_count=0,
                    error_message="No soil data found for location",
                    execution_time_ms=execution_time,
                    reliability_score=0.0
                )
                
        except Exception as e:
            logger.error(f"Error collecting soil health data: {e}")
            return DataCollectionResult(
                source_name="Soil Health Service",
                data_type="soil_health",
                success=False,
                data_count=0,
                error_message=str(e),
                execution_time_ms=0.0,
                reliability_score=0.0
            )
    
    async def _collect_crop_calendar_data(self, farmer_profile: Dict[str, Any]) -> DataCollectionResult:
        """Collect crop calendar data"""
        try:
            start_time = datetime.now()
            
            # Get location and crop preferences
            state = farmer_profile.get("state", "Karnataka")  # Default to Karnataka
            crop_preferences = farmer_profile.get("crop_preferences", [])
            
            # Collect calendars for available crops and seasons
            calendars = []
            
            # Get calendars for major seasons
            seasons = [Season.KHARIF, Season.RABI]
            
            for season in seasons:
                # Get available crops for this season
                available_crops = await self.crop_calendar_service.get_available_crops(state, season)
                
                # Get calendars for preferred crops
                for crop_name in crop_preferences[:3]:  # Limit to top 3 preferences
                    if crop_name in available_crops:
                        calendar = await self.crop_calendar_service.get_crop_calendar(
                            crop_name=crop_name,
                            region=state,
                            season=season
                        )
                        if calendar:
                            calendars.append(calendar)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return DataCollectionResult(
                source_name="Crop Calendar Service",
                data_type="crop_calendar",
                success=True,
                data_count=len(calendars),
                execution_time_ms=execution_time,
                reliability_score=0.95 if calendars else 0.0
            )
            
        except Exception as e:
            logger.error(f"Error collecting crop calendar data: {e}")
            return DataCollectionResult(
                source_name="Crop Calendar Service",
                data_type="crop_calendar",
                success=False,
                data_count=0,
                error_message=str(e),
                execution_time_ms=0.0,
                reliability_score=0.0
            )
    
    async def _collect_scheme_data(self, farmer_profile: Dict[str, Any]) -> DataCollectionResult:
        """Collect government scheme data"""
        try:
            start_time = datetime.now()
            
            # Find eligible schemes for the farmer
            eligible_schemes = await self.scheme_service.find_eligible_schemes(farmer_profile)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return DataCollectionResult(
                source_name="Scheme Matching Service",
                data_type="government_schemes",
                success=True,
                data_count=len(eligible_schemes),
                execution_time_ms=execution_time,
                reliability_score=0.95 if eligible_schemes else 0.0
            )
            
        except Exception as e:
            logger.error(f"Error collecting scheme data: {e}")
            return DataCollectionResult(
                source_name="Scheme Matching Service",
                data_type="government_schemes",
                success=False,
                data_count=0,
                error_message=str(e),
                execution_time_ms=0.0,
                reliability_score=0.0
            )
    
    async def _create_unified_data(
        self, 
        farmer_profile: Dict[str, Any], 
        collection_results: Dict[str, DataCollectionResult]
    ) -> UnifiedFarmerData:
        """Create unified data structure from collection results"""
        try:
            # Extract data from results
            soil_data = None
            if collection_results.get("soil_health", {}).get("success"):
                # Get soil data from service
                pincode = farmer_profile.get("pincode")
                if pincode:
                    soil_data = await self.soil_service.get_soil_data_by_pincode(pincode)
            
            crop_calendars = []
            if collection_results.get("crop_calendar", {}).get("success"):
                # Get crop calendars
                state = farmer_profile.get("state", "Karnataka")
                crop_preferences = farmer_profile.get("crop_preferences", ["rice", "wheat"])
                
                for crop_name in crop_preferences[:2]:  # Top 2 preferences
                    for season in [Season.KHARIF, Season.RABI]:
                        calendar = await self.crop_calendar_service.get_crop_calendar(
                            crop_name=crop_name,
                            region=state,
                            season=season
                        )
                        if calendar:
                            crop_calendars.append(calendar)
            
            eligible_schemes = []
            if collection_results.get("government_schemes", {}).get("success"):
                # Get eligible schemes
                eligible_schemes = await self.scheme_service.find_eligible_schemes(farmer_profile)
            
            # Calculate overall reliability score
            reliability_scores = [
                result.reliability_score 
                for result in collection_results.values() 
                if result.success
            ]
            overall_reliability = sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.0
            
            return UnifiedFarmerData(
                farmer_id=farmer_profile.get("client_id", "unknown"),
                location={
                    "lat": farmer_profile.get("lat", 0.0),
                    "lng": farmer_profile.get("lon", 0.0)
                },
                pincode=farmer_profile.get("pincode", ""),
                district=farmer_profile.get("district", ""),
                state=farmer_profile.get("state", ""),
                soil_health=soil_data,
                crop_calendars=crop_calendars,
                eligible_schemes=eligible_schemes,
                last_updated=datetime.now(),
                data_reliability_score=overall_reliability
            )
            
        except Exception as e:
            logger.error(f"Error creating unified data: {e}")
            return await self._create_partial_data(farmer_profile)
    
    async def _create_partial_data(self, farmer_profile: Dict[str, Any]) -> UnifiedFarmerData:
        """Create partial data structure when full collection fails"""
        try:
            return UnifiedFarmerData(
                farmer_id=farmer_profile.get("client_id", "unknown"),
                location={
                    "lat": farmer_profile.get("lat", 0.0),
                    "lng": farmer_profile.get("lon", 0.0)
                },
                pincode=farmer_profile.get("pincode", ""),
                district=farmer_profile.get("district", ""),
                state=farmer_profile.get("state", ""),
                soil_health=None,
                crop_calendars=[],
                eligible_schemes=[],
                last_updated=datetime.now(),
                data_reliability_score=0.0
            )
            
        except Exception as e:
            logger.error(f"Error creating partial data: {e}")
            # Return minimal data structure
            return UnifiedFarmerData(
                farmer_id="unknown",
                location={"lat": 0.0, "lng": 0.0},
                pincode="",
                district="",
                state="",
                soil_health=None,
                crop_calendars=[],
                eligible_schemes=[],
                last_updated=datetime.now(),
                data_reliability_score=0.0
            )
    
    def _is_cache_valid(self, farmer_id: str) -> bool:
        """Check if cached data is still valid"""
        try:
            if farmer_id not in self.cache_timestamps:
                return False
            
            cache_time = self.cache_timestamps[farmer_id]
            cache_age = datetime.now() - cache_time
            max_age = timedelta(hours=self.cache_duration_hours)
            
            return cache_age < max_age
            
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    def _cache_data(self, farmer_id: str, data: UnifiedFarmerData):
        """Cache collected data"""
        try:
            self.data_cache[farmer_id] = data
            self.cache_timestamps[farmer_id] = datetime.now()
            
            # Limit cache size
            if len(self.data_cache) > 1000:  # Max 1000 farmers
                # Remove oldest entries
                oldest_id = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
                del self.data_cache[oldest_id]
                del self.cache_timestamps[oldest_id]
                
        except Exception as e:
            logger.error(f"Error caching data: {e}")
    
    async def get_data_collection_status(self, farmer_id: str) -> Dict[str, Any]:
        """Get status of data collection for a farmer"""
        try:
            cache_valid = self._is_cache_valid(farmer_id)
            cached_data = self.data_cache.get(farmer_id)
            
            status = {
                "farmer_id": farmer_id,
                "cache_valid": cache_valid,
                "has_cached_data": cached_data is not None,
                "last_updated": cached_data.last_updated.isoformat() if cached_data else None,
                "data_reliability_score": cached_data.data_reliability_score if cached_data else 0.0,
                "data_summary": {
                    "soil_health": cached_data.soil_health is not None if cached_data else False,
                    "crop_calendars": len(cached_data.crop_calendars) if cached_data else 0,
                    "eligible_schemes": len(cached_data.eligible_schemes) if cached_data else 0
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting data collection status: {e}")
            return {
                "farmer_id": farmer_id,
                "error": str(e)
            }
    
    async def refresh_farmer_data(self, farmer_id: str) -> bool:
        """Force refresh of cached data for a farmer"""
        try:
            # Remove from cache to force refresh
            if farmer_id in self.data_cache:
                del self.data_cache[farmer_id]
            if farmer_id in self.cache_timestamps:
                del self.cache_timestamps[farmer_id]
            
            logger.info(f"Cache cleared for farmer {farmer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing farmer data: {e}")
            return False
    
    async def export_farmer_data(self, farmer_id: str, filename: str) -> bool:
        """Export collected farmer data to JSON file"""
        try:
            cached_data = self.data_cache.get(farmer_id)
            if not cached_data:
                logger.warning(f"No cached data found for farmer {farmer_id}")
                return False
            
            # Convert to JSON-serializable format
            export_data = {
                "farmer_id": cached_data.farmer_id,
                "location": cached_data.location,
                "pincode": cached_data.pincode,
                "district": cached_data.district,
                "state": cached_data.state,
                "soil_health": {
                    "pincode": cached_data.soil_health.pincode,
                    "district": cached_data.soil_health.district,
                    "state": cached_data.soil_health.state,
                    "soil_type": cached_data.soil_health.soil_type,
                    "ph_level": cached_data.soil_health.ph_level,
                    "organic_carbon": cached_data.soil_health.organic_carbon,
                    "nitrogen_n": cached_data.soil_health.nitrogen_n,
                    "phosphorus_p": cached_data.soil_health.phosphorus_p,
                    "potassium_k": cached_data.soil_health.potassium_k,
                    "source": cached_data.soil_health.source,
                    "reliability_score": cached_data.soil_health.reliability_score
                } if cached_data.soil_health else None,
                "crop_calendars": [
                    {
                        "crop_name": cal.crop_name,
                        "crop_variety": cal.crop_variety,
                        "region": cal.region,
                        "season": cal.season.value,
                        "total_duration_days": cal.total_duration_days,
                        "optimal_planting_start": cal.optimal_planting_start.isoformat() if cal.optimal_planting_start else None,
                        "optimal_planting_end": cal.optimal_planting_end.isoformat() if cal.optimal_planting_end else None,
                        "expected_harvest_start": cal.expected_harvest_start.isoformat() if cal.expected_harvest_start else None,
                        "expected_harvest_end": cal.expected_harvest_end.isoformat() if cal.expected_harvest_end else None,
                        "source": cal.source,
                        "reliability_score": cal.reliability_score
                    } for cal in cached_data.crop_calendars
                ],
                "eligible_schemes": [
                    {
                        "scheme_name": match.scheme.scheme_name,
                        "category": match.scheme.category.value,
                        "match_score": match.match_score,
                        "application_status": match.application_status,
                        "estimated_benefit": match.estimated_benefit,
                        "match_reasons": match.match_reasons,
                        "next_steps": match.next_steps
                    } for match in cached_data.eligible_schemes
                ],
                "last_updated": cached_data.last_updated.isoformat(),
                "data_reliability_score": cached_data.data_reliability_score
            }
            
            # Write to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported farmer data to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting farmer data: {e}")
            return False

# Example usage and testing
async def test_data_collection_coordinator():
    """Test the data collection coordinator"""
    async with DataCollectionCoordinator() as coordinator:
        # Test farmer profile
        farmer_profile = {
            "client_id": "test_farmer_001",
            "pincode": "560001",
            "lat": 12.9716,
            "lon": 77.5946,
            "district": "Bangalore",
            "state": "Karnataka",
            "crop_preferences": ["rice", "wheat", "maize"]
        }
        
        # Collect comprehensive data
        print("Collecting comprehensive farmer data...")
        unified_data = await coordinator.collect_comprehensive_farmer_data(farmer_profile)
        
        print(f"\nData collection completed for farmer {unified_data.farmer_id}")
        print(f"Location: {unified_data.district}, {unified_data.state}")
        print(f"Data reliability score: {unified_data.data_reliability_score:.2f}")
        
        if unified_data.soil_health:
            print(f"\nSoil Health Data:")
            print(f"  Soil Type: {unified_data.soil_health.soil_type}")
            print(f"  pH Level: {unified_data.soil_health.ph_level}")
            print(f"  Organic Carbon: {unified_data.soil_health.organic_carbon}%")
        
        print(f"\nCrop Calendars: {len(unified_data.crop_calendars)}")
        for calendar in unified_data.crop_calendars[:2]:  # Show first 2
            print(f"  {calendar.crop_name} ({calendar.season.value}): {calendar.total_duration_days} days")
        
        print(f"\nEligible Schemes: {len(unified_data.eligible_schemes)}")
        for scheme_match in unified_data.eligible_schemes[:2]:  # Show first 2
            print(f"  {scheme_match.scheme.scheme_name}: Score {scheme_match.match_score:.2f}")
        
        # Get collection status
        status = await coordinator.get_data_collection_status(farmer_profile["client_id"])
        print(f"\nCollection Status: {status}")
        
        # Export data
        export_success = await coordinator.export_farmer_data(
            farmer_profile["client_id"], 
            "farmer_data_export.json"
        )
        print(f"\nData export: {'Success' if export_success else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(test_data_collection_coordinator())
