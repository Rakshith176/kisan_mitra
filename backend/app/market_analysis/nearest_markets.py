from __future__ import annotations

from dataclasses import dataclass
from math import radians, cos, sin, asin, sqrt
from typing import Iterable, List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Mandi:
    name: str
    lat: float
    lon: float
    district: str | None = None
    state: str | None = None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = rlon2 - rlon1
    dlat = rlat2 - rlat1
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371.0 * c


def pick_nearest_mandis(
    *, user_lat: float, user_lon: float, mandis: Iterable[Mandi], k: int = 5
) -> List[Mandi]:
    return sorted(mandis, key=lambda m: _haversine_km(user_lat, user_lon, m.lat, m.lon))[:k]


class NearestMarketsService:
    """Service for finding nearest markets to a given location using real market data"""
    
    def __init__(self):
        # Import market clients
        from .karnataka_client import KarnatakaClient
        from .agmarknet_client import AgmarknetClient
        
        self.karnataka_client = KarnatakaClient()
        self.agmarknet_client = AgmarknetClient()
        
        # Cache for market data
        self.market_cache = {}
        self.cache_duration_hours = 24
        
    async def _get_market_data_from_sources(self) -> List[Mandi]:
        """Get market data from multiple sources"""
        try:
            mandis = []
            
            # Get data from Karnataka government website
            try:
                karnataka_prices = await self.karnataka_client.get_market_prices_from_main_page()
                if karnataka_prices:
                    # Extract unique markets from price data
                    karnataka_markets = set()
                    for price in karnataka_prices:
                        if price.market and price.market != "State Level":
                            karnataka_markets.add(price.market)
                    
                    # Convert to Mandi objects with estimated coordinates
                    for market_name in karnataka_markets:
                        district = self._extract_district_from_market_name(market_name)
                        coordinates = self._get_coordinates_for_district(district)
                        
                        mandi = Mandi(
                            name=market_name,
                            lat=coordinates["lat"],
                            lon=coordinates["lon"],
                            district=district,
                            state="Karnataka"
                        )
                        mandis.append(mandi)
                        
                    logger.info(f"Found {len(mandis)} markets from Karnataka data")
            except Exception as e:
                logger.warning(f"Failed to fetch Karnataka market data: {e}")
            
            # Get data from Agmarknet (if available)
            try:
                # Try to get market list from Agmarknet
                agmarknet_markets = await self._get_agmarknet_markets()
                if agmarknet_markets:
                    for market_data in agmarknet_markets:
                        mandi = Mandi(
                            name=market_data.get("mandi_name", "Unknown"),
                            lat=market_data.get("lat", 0.0),
                            lon=market_data.get("lon", 0.0),
                            district=market_data.get("district", "Unknown"),
                            state=market_data.get("state", "Unknown")
                        )
                        mandis.append(mandi)
                        
                    logger.info(f"Found {len(agmarknet_markets)} markets from Agmarknet")
            except Exception as e:
                logger.warning(f"Failed to fetch Agmarknet market data: {e}")
            
            # If no data from sources, use fallback coordinates for major districts
            if not mandis:
                logger.warning("No market data from sources, using fallback coordinates")
                mandis = self._get_fallback_mandi_data()
            
            return mandis
            
        except Exception as e:
            logger.error(f"Error getting market data from sources: {e}")
            return self._get_fallback_mandi_data()
    
    async def _get_agmarknet_markets(self) -> List[Dict[str, Any]]:
        """Get market list from Agmarknet"""
        try:
            # Try to get markets for a common crop to extract market list
            wheat_prices = await self.agmarknet_client.get_market_prices("wheat")
            
            markets = []
            for price in wheat_prices:
                market_info = {
                    "mandi_name": price.get("mandi_name", ""),
                    "district": price.get("district", ""),
                    "state": price.get("state", ""),
                    "lat": price.get("lat", 0.0),
                    "lon": price.get("lon", 0.0)
                }
                
                # Only add if we have valid coordinates
                if market_info["lat"] and market_info["lon"]:
                    markets.append(market_info)
            
            return markets
            
        except Exception as e:
            logger.warning(f"Failed to get Agmarknet markets: {e}")
            return []
    
    def _extract_district_from_market_name(self, market_name: str) -> str:
        """Extract district from market name"""
        # Common Karnataka districts
        districts = [
            "Bangalore", "Mysore", "Mangalore", "Belgaum", "Gulbarga", 
            "Dharwad", "Bellary", "Bijapur", "Raichur", "Kolar",
            "Tumkur", "Mandya", "Hassan", "Shimoga", "Chitradurga",
            "Davangere", "Udupi", "Kodagu", "Chikkamagaluru", "Bagalkot"
        ]
        
        for district in districts:
            if district.lower() in market_name.lower():
                return district
        
        return "Unknown"
    
    def _get_coordinates_for_district(self, district: str) -> Dict[str, float]:
        """Get coordinates for a district"""
        # District coordinates in Karnataka
        district_coordinates = {
            "Bangalore": {"lat": 12.9716, "lon": 77.5946},
            "Mysore": {"lat": 12.2958, "lon": 76.6394},
            "Mangalore": {"lat": 12.9141, "lon": 74.8560},
            "Belgaum": {"lat": 15.8497, "lon": 74.4977},
            "Gulbarga": {"lat": 17.3297, "lon": 76.8343},
            "Dharwad": {"lat": 15.4589, "lon": 75.0078},
            "Bellary": {"lat": 15.1394, "lon": 76.9214},
            "Bijapur": {"lat": 16.8248, "lon": 75.7156},
            "Raichur": {"lat": 16.2076, "lon": 77.3563},
            "Kolar": {"lat": 13.1367, "lon": 78.1328},
            "Tumkur": {"lat": 13.3409, "lon": 77.1018},
            "Mandya": {"lat": 12.5244, "lon": 76.8958},
            "Hassan": {"lat": 13.0034, "lon": 76.1004},
            "Shimoga": {"lat": 13.9299, "lon": 75.5681},
            "Chitradurga": {"lat": 14.2261, "lon": 76.4002},
            "Davangere": {"lat": 14.4644, "lon": 75.9218},
            "Udupi": {"lat": 13.3409, "lon": 74.7421},
            "Kodagu": {"lat": 12.3375, "lon": 75.8069},
            "Chikkamagaluru": {"lat": 13.3161, "lon": 75.7720},
            "Bagalkot": {"lat": 16.1869, "lon": 75.6961}
        }
        
        return district_coordinates.get(district, {"lat": 12.9716, "lon": 77.5946})  # Default to Bangalore
    
    def _get_fallback_mandi_data(self) -> List[Mandi]:
        """Fallback mandi data when sources are unavailable"""
        # Only include major markets with verified coordinates
        return [
            Mandi("APMC Bangalore", 12.9716, 77.5946, "Bangalore", "Karnataka"),
            Mandi("APMC Mysore", 12.2958, 76.6394, "Mysore", "Karnataka"),
            Mandi("APMC Mandya", 12.5244, 76.8958, "Mandya", "Karnataka"),
            Mandi("APMC Hassan", 13.0034, 76.1004, "Hassan", "Karnataka"),
            Mandi("APMC Tumkur", 13.3409, 77.1018, "Tumkur", "Karnataka"),
            Mandi("APMC Kolar", 13.1367, 78.1328, "Kolar", "Karnataka"),
        ]
    
    async def find_nearest_markets(
        self, 
        latitude: float, 
        longitude: float, 
        crop_name: str = None,
        max_distance_km: float = 200.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find nearest markets to a given location using real market data
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            crop_name: Optional crop name to filter markets
            max_distance_km: Maximum distance to search (default: 200 km)
            limit: Maximum number of markets to return (default: 10)
            
        Returns:
            List of nearest markets with distance information
        """
        try:
            # Get market data from sources (with caching)
            cache_key = f"markets_{crop_name or 'all'}"
            
            if cache_key not in self.market_cache:
                # Fetch fresh market data
                mandis = await self._get_market_data_from_sources()
                self.market_cache[cache_key] = {
                    "data": mandis,
                    "timestamp": datetime.now()
                }
            else:
                # Check if cache is still valid
                cache_age = datetime.now() - self.market_cache[cache_key]["timestamp"]
                if cache_age.total_seconds() > (self.cache_duration_hours * 3600):
                    # Cache expired, fetch fresh data
                    mandis = await self._get_market_data_from_sources()
                    self.market_cache[cache_key] = {
                        "data": mandis,
                        "timestamp": datetime.now()
                    }
                else:
                    # Use cached data
                    mandis = self.market_cache[cache_key]["data"]
            
            # Filter mandis by distance
            nearby_mandis = []
            
            for mandi in mandis:
                distance = _haversine_km(latitude, longitude, mandi.lat, mandi.lon)
                
                if distance <= max_distance_km:
                    nearby_mandis.append({
                        "mandi": mandi,
                        "distance_km": round(distance, 2)
                    })
            
            # Sort by distance
            nearby_mandis.sort(key=lambda x: x["distance_km"])
            
            # Limit results
            nearby_mandis = nearby_mandis[:limit]
            
            # Convert to response format
            result = []
            for item in nearby_mandis:
                mandi = item["mandi"]
                result.append({
                    "mandi_name": mandi.name,
                    "latitude": mandi.lat,
                    "longitude": mandi.lon,
                    "district": mandi.district,
                    "state": mandi.state,
                    "distance_km": item["distance_km"],
                    "estimated_travel_time_hours": self._estimate_travel_time(item["distance_km"]),
                    "transport_cost_estimate": self._estimate_transport_cost(item["distance_km"]),
                    "crop_availability": await self._get_crop_availability_from_sources(mandi, crop_name)
                })
            
            logger.info(f"Found {len(result)} nearby markets within {max_distance_km}km")
            return result
            
        except Exception as e:
            logger.error(f"Error finding nearest markets: {e}")
            return []
    
    def _estimate_travel_time(self, distance_km: float) -> float:
        """Estimate travel time in hours based on distance"""
        # Assume average speed of 40 km/h for rural roads
        avg_speed_kmh = 40.0
        travel_time_hours = distance_km / avg_speed_kmh
        
        # Add buffer for loading/unloading and road conditions
        buffer_hours = 0.5
        return round(travel_time_hours + buffer_hours, 1)
    
    def _estimate_transport_cost(self, distance_km: float) -> Dict[str, Any]:
        """Estimate transport cost based on distance"""
        # Base cost per km (varies by transport type)
        truck_cost_per_km = 8.0  # ₹8 per km for truck
        tractor_cost_per_km = 5.0  # ₹5 per km for tractor
        
        # Calculate costs
        truck_cost = distance_km * truck_cost_per_km * 2  # Round trip
        tractor_cost = distance_km * tractor_cost_per_km * 2  # Round trip
        
        return {
            "truck_round_trip": round(truck_cost, 2),
            "tractor_round_trip": round(tractor_cost, 2),
            "cost_per_quintal_truck": round(truck_cost / 10, 2),  # Assuming 10 quintal capacity
            "cost_per_quintal_tractor": round(tractor_cost / 5, 2),  # Assuming 5 quintal capacity
            "currency": "INR"
        }
    
    async def _get_crop_availability_from_sources(self, mandi: Mandi, crop_name: str = None) -> Dict[str, Any]:
        """Get crop availability information for a mandi using real market data"""
        try:
            if crop_name:
                # Get real price data for the specific crop at this mandi
                try:
                    # Try Karnataka client first
                    karnataka_prices = await self.karnataka_client.get_market_prices_from_main_page()
                    
                    # Filter prices for this mandi and crop
                    mandi_prices = [
                        p for p in karnataka_prices 
                        if p.market == mandi.name and crop_name.lower() in p.commodity.lower()
                    ]
                    
                    if mandi_prices:
                        # Calculate price statistics from real data
                        prices = [p.modal for p in mandi_prices if p.modal > 0]
                        if prices:
                            avg_price = sum(prices) / len(prices)
                            min_price = min(prices)
                            max_price = max(prices)
                            
                            return {
                                "crop_name": crop_name,
                                "available": True,
                                "peak_season": self._get_peak_season(crop_name),
                                "typical_volume": f"{len(mandi_prices)} varieties available",
                                "price_range": f"₹{min_price:.0f}-₹{max_price:.0f} per quintal",
                                "average_price": f"₹{avg_price:.0f} per quintal",
                                "data_source": "Karnataka Government Portal",
                                "last_updated": datetime.now().isoformat()
                            }
                    
                    # Try Agmarknet as fallback
                    agmarknet_prices = await self.agmarknet_client.get_market_prices(crop_name, mandi.state, mandi.district)
                    if agmarknet_prices:
                        prices = [p.get("modal_price", 0) for p in agmarknet_prices if p.get("modal_price", 0) > 0]
                        if prices:
                            avg_price = sum(prices) / len(prices)
                            min_price = min(prices)
                            max_price = max(prices)
                            
                            return {
                                "crop_name": crop_name,
                                "available": True,
                                "peak_season": self._get_peak_season(crop_name),
                                "typical_volume": f"{len(agmarknet_prices)} markets available",
                                "price_range": f"₹{min_price:.0f}-₹{max_price:.0f} per quintal",
                                "average_price": f"₹{avg_price:.0f} per quintal",
                                "data_source": "Agmarknet",
                                "last_updated": datetime.now().isoformat()
                            }
                            
                except Exception as e:
                    logger.warning(f"Failed to get real crop availability for {crop_name} at {mandi.name}: {e}")
                
                # Fallback to basic information
                return {
                    "crop_name": crop_name,
                    "available": True,
                    "peak_season": self._get_peak_season(crop_name),
                    "typical_volume": "Data not available",
                    "price_range": "Check current prices",
                    "data_source": "Fallback data"
                }
            else:
                # Get general availability for the mandi
                try:
                    # Get all crops available at this mandi from Karnataka data
                    karnataka_prices = await self.karnataka_client.get_market_prices_from_main_page()
                    
                    # Filter prices for this mandi
                    mandi_prices = [p for p in karnataka_prices if p.market == mandi.name]
                    
                    if mandi_prices:
                        # Extract unique crops
                        crops = list(set([p.commodity for p in mandi_prices if p.commodity]))
                        
                        return {
                            "major_crops": crops[:10],  # Top 10 crops
                            "peak_trading_hours": "6:00 AM - 2:00 PM",
                            "market_days": "Monday to Saturday",
                            "facilities": self._get_mandi_facilities(mandi),
                            "data_source": "Karnataka Government Portal",
                            "last_updated": datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.warning(f"Failed to get general availability for {mandi.name}: {e}")
                
                # Fallback to basic information
                return {
                    "major_crops": ["rice", "wheat", "maize", "pulses", "oilseeds"],
                    "peak_trading_hours": "6:00 AM - 2:00 PM",
                    "market_days": "Monday to Saturday",
                    "facilities": self._get_mandi_facilities(mandi),
                    "data_source": "Fallback data"
                }
                
        except Exception as e:
            logger.error(f"Error getting crop availability: {e}")
            return {
                "error": str(e),
                "data_source": "Error"
            }
    
    def _get_crop_availability(self, mandi: Mandi, crop_name: str = None) -> Dict[str, Any]:
        """Legacy method - kept for backward compatibility"""
        # This would typically come from a database or API
        # For now, return sample data
        
        if crop_name:
            # Return specific crop availability
            return {
                "crop_name": crop_name,
                "available": True,
                "peak_season": self._get_peak_season(crop_name),
                "typical_volume": "1000-5000 quintals daily",
                "price_range": "₹2000-₹4000 per quintal"
            }
        else:
            # Return general availability
            return {
                "major_crops": ["rice", "wheat", "maize", "pulses", "oilseeds"],
                "peak_trading_hours": "6:00 AM - 2:00 PM",
                "market_days": "Monday to Saturday",
                "facilities": ["weighing", "storage", "parking", "canteen"]
            }
    
    def _get_peak_season(self, crop_name: str) -> str:
        """Get peak season for a crop"""
        crop_seasons = {
            "rice": "October-December (Kharif harvest)",
            "wheat": "March-May (Rabi harvest)",
            "maize": "September-October (Kharif harvest)",
            "pulses": "February-March (Rabi harvest)",
            "oilseeds": "February-March (Rabi harvest)"
        }
        return crop_seasons.get(crop_name.lower(), "Year-round")
    
    async def get_market_details(self, mandi_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific mandi"""
        try:
            # Get fresh market data to ensure it's up-to-date
            mandis = await self._get_market_data_from_sources()
            for mandi in mandis:
                if mandi.name.lower() == mandi_name.lower():
                    return {
                        "mandi_name": mandi.name,
                        "latitude": mandi.lat,
                        "longitude": mandi.lon,
                        "district": mandi.district,
                        "state": mandi.state,
                        "contact_info": self._get_mandi_contact_info(mandi),
                        "facilities": self._get_mandi_facilities(mandi),
                        "operating_hours": "6:00 AM - 2:00 PM",
                        "market_days": "Monday to Saturday",
                        "peak_hours": "8:00 AM - 12:00 PM"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting market details: {e}")
            return None
    
    def _get_mandi_contact_info(self, mandi: Mandi) -> Dict[str, str]:
        """Get contact information for a mandi"""
        # This would typically come from a database
        # For now, return sample data
        return {
            "phone": "+91-80-2222-XXXX",  # Sample number
            "email": f"apmc.{mandi.district.lower()}@karnataka.gov.in",
            "address": f"APMC {mandi.district}, {mandi.state}",
            "website": f"https://apmc.{mandi.district.lower()}.karnataka.gov.in"
        }
    
    def _get_mandi_facilities(self, mandi: Mandi) -> List[str]:
        """Get facilities available at a mandi"""
        # This would typically come from a database
        # For now, return sample data
        base_facilities = ["weighing", "storage", "parking", "canteen", "restrooms"]
        
        # Add district-specific facilities
        if mandi.district == "Bangalore":
            base_facilities.extend(["cold_storage", "quality_lab", "banking", "atm"])
        elif mandi.district == "Mysore":
            base_facilities.extend(["quality_lab", "banking", "atm"])
        
        return base_facilities
    
    async def search_markets_by_crop(self, crop_name: str, state: str = None) -> List[Dict[str, Any]]:
        """Search for markets that trade a specific crop using real data"""
        try:
            # Get fresh market data
            mandis = await self._get_market_data_from_sources()
            matching_markets = []
            
            for mandi in mandis:
                # Filter by state if specified
                if state and mandi.state.lower() != state.lower():
                    continue
                
                # Check if mandi trades this crop using real data
                if await self._mandi_trades_crop_real(mandi, crop_name):
                    matching_markets.append({
                        "mandi_name": mandi.name,
                        "district": mandi.district,
                        "state": mandi.state,
                        "latitude": mandi.lat,
                        "longitude": mandi.lon,
                        "crop_specialization": self._get_crop_specialization(mandi, crop_name),
                        "trading_volume": await self._get_trading_volume_real(mandi, crop_name)
                    })
            
            logger.info(f"Found {len(matching_markets)} markets trading {crop_name}")
            return matching_markets
            
        except Exception as e:
            logger.error(f"Error searching markets by crop: {e}")
            return []
    
    async def _mandi_trades_crop_real(self, mandi: Mandi, crop_name: str) -> bool:
        """Check if a mandi trades a specific crop using real data"""
        try:
            # Check Karnataka data first
            karnataka_prices = await self.karnataka_client.get_market_prices_from_main_page()
            mandi_crops = [p.commodity for p in karnataka_prices if p.market == mandi.name]
            
            if any(crop_name.lower() in crop.lower() for crop in mandi_crops):
                return True
            
            # Check Agmarknet data as fallback
            agmarknet_prices = await self.agmarknet_client.get_market_prices(crop_name, mandi.state, mandi.district)
            if agmarknet_prices:
                return True
            
            # Fallback to basic logic
            return self._mandi_trades_crop_fallback(mandi, crop_name)
            
        except Exception as e:
            logger.warning(f"Failed to check real crop availability: {e}")
            return self._mandi_trades_crop_fallback(mandi, crop_name)
    
    def _mandi_trades_crop_fallback(self, mandi: Mandi, crop_name: str) -> bool:
        """Fallback method to check if a mandi trades a specific crop"""
        # This would typically come from a database
        # For now, use simplified logic based on district
        major_crops = ["rice", "wheat", "maize", "pulses", "oilseeds"]
        
        if crop_name.lower() in major_crops:
            return True
        
        # District-specific crop specializations
        district_crops = {
            "Bangalore": ["vegetables", "fruits", "flowers"],
            "Mysore": ["rice", "sugarcane", "coconut"],
            "Mandya": ["rice", "sugarcane"],
            "Hassan": ["coffee", "cardamom", "pepper"]
        }
        
        if mandi.district in district_crops:
            return crop_name.lower() in district_crops[mandi.district]
        
        return True  # Default to True for major mandis
    
    def _get_crop_specialization(self, mandi: Mandi, crop_name: str) -> str:
        """Get crop specialization level for a mandi"""
        # This would typically come from a database
        # For now, return sample data
        if mandi.district == "Bangalore":
            return "Major trading center for all crops"
        elif mandi.district in ["Mysore", "Mandya"]:
            return "Specialized in rice and sugarcane"
        elif mandi.district == "Hassan":
            return "Specialized in plantation crops"
        else:
            return "General agricultural market"
    
    async def _get_trading_volume_real(self, mandi: Mandi, crop_name: str) -> str:
        """Get trading volume information for a crop at a mandi using real data"""
        try:
            # Try to get real trading volume from Karnataka data
            karnataka_prices = await self.karnataka_client.get_market_prices_from_main_page()
            
            # Filter prices for this mandi and crop
            mandi_crop_prices = [
                p for p in karnataka_prices 
                if p.market == mandi.name and crop_name.lower() in p.commodity.lower()
            ]
            
            if mandi_crop_prices:
                # Calculate total arrivals if available
                total_arrivals = sum(p.arrivals for p in mandi_crop_prices if p.arrivals)
                if total_arrivals > 0:
                    return f"{total_arrivals} quintals daily"
                else:
                    return f"{len(mandi_crop_prices)} varieties available"
            
            # Fallback to estimated volumes
            return self._get_trading_volume_fallback(mandi, crop_name)
            
        except Exception as e:
            logger.warning(f"Failed to get real trading volume: {e}")
            return self._get_trading_volume_fallback(mandi, crop_name)
    
    def _get_trading_volume_fallback(self, mandi: Mandi, crop_name: str) -> str:
        """Fallback method for trading volume information"""
        # This would typically come from a database
        # For now, return sample data
        if mandi.district == "Bangalore":
            return "5000-10000 quintals daily"
        elif mandi.district in ["Mysore", "Mandya"]:
            return "2000-5000 quintals daily"
        else:
            return "1000-3000 quintals daily"
    
    async def clear_cache(self):
        """Clear the market data cache"""
        try:
            self.market_cache.clear()
            logger.info("Market data cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status information"""
        try:
            cache_info = {}
            for key, value in self.market_cache.items():
                cache_age = datetime.now() - value["timestamp"]
                cache_info[key] = {
                    "entries": len(value["data"]),
                    "age_hours": round(cache_age.total_seconds() / 3600, 2),
                    "expires_in_hours": max(0, self.cache_duration_hours - round(cache_age.total_seconds() / 3600, 2))
                }
            
            return {
                "cache_entries": len(self.market_cache),
                "cache_duration_hours": self.cache_duration_hours,
                "cache_details": cache_info
            }
            
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return {"error": str(e)}


