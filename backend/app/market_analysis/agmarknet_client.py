from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import httpx

from ..config import settings
from .schemas import MandiPriceRow


class AgmarknetClient:
    """Client for Agmarknet market data API"""
    
    def __init__(self):
        pass
    
    async def get_market_prices(self, commodity: str, state: str = None, district: str = None) -> List[Dict[str, Any]]:
        """
        Get market prices for a commodity
        
        Args:
            commodity: Name of the commodity
            state: State name (optional)
            district: District name (optional)
            
        Returns:
            List of market price data
        """
        try:
            # First try to get real data from the API
            real_data = await self._fetch_real_market_data(commodity, state, district)
            
            if real_data:
                return real_data
            
            # If no real data, fall back to mock data for testing
            print(f"⚠️ No real market data found for {commodity}, using mock data for testing")
            return [] # Removed mock data fallbacks
            
        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            # Fall back to mock data
            return [] # Removed mock data fallbacks
    
    async def get_price_trends(self, commodity: str, state: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get price trends for a commodity
        
        Args:
            commodity: Name of the commodity
            state: State name (optional)
            days: Number of days to analyze
            
        Returns:
            Price trend analysis
        """
        try:
            # For now, use mock data for trends
            return {} # Removed mock data fallbacks
        except Exception as e:
            print(f"❌ Error fetching price trends: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch price trends: {e}"
            }
    
    async def get_market_recommendations(self, commodity: str, state: str = None, district: str = None) -> Dict[str, Any]:
        """
        Get market recommendations for a commodity
        
        Args:
            commodity: Name of the commodity
            state: State name (optional)
            district: District name (optional)
            
        Returns:
            Market recommendations
        """
        try:
            return {} # Removed mock data fallbacks
        except Exception as e:
            print(f"❌ Error fetching market recommendations: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch market recommendations: {e}"
            }
    
    async def _fetch_real_market_data(self, commodity: str, state: str = None, district: str = None) -> List[Dict[str, Any]]:
        """
        Fetch real market data from the API
        
        Args:
            commodity: Name of the commodity
            state: State name (optional)
            district: District name (optional)
            
        Returns:
            List of market price data or empty list if no data
        """
        try:
            url = f"{settings.agmarknet_base_url}{settings.agmarknet_resource_id}"
            
            params = {
                "api-key": settings.data_gov_in_api_key,
                "format": "json",
                "limit": 100,
                "from_date": (date.today() - timedelta(days=90)).isoformat(),
                "to_date": date.today().isoformat(),
            }
            
            # Add filters if provided
            if commodity:
                params["filters[commodity]"] = commodity
            if state:
                params["filters[state]"] = state
            if district:
                params["filters[district]"] = district
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, params=params)
                
                if resp.status_code == 200:
                    data = resp.json()
                    records = data.get("records", [])
                    
                    if records:
                        # Convert API response to our format
                        converted_records = []
                        for record in records:
                            try:
                                converted_record = {
                                    "mandi_name": record.get("Market", "Unknown"),
                                    "state": record.get("State", "Unknown"),
                                    "district": record.get("District", "Unknown"),
                                    "commodity": record.get("Commodity", commodity),
                                    "variety": record.get("Variety", "Unknown"),
                                    "min_price": float(record.get("Min_Price", 0)),
                                    "max_price": float(record.get("Max_Price", 0)),
                                    "modal_price": float(record.get("Modal_Price", 0)),
                                    "date": record.get("Arrival_Date", date.today().isoformat()),
                                    "commodity_code": record.get("Commodity_Code", "")
                                }
                                converted_records.append(converted_record)
                            except (ValueError, TypeError) as e:
                                print(f"⚠️ Skipping invalid record: {e}")
                                continue
                        
                        return converted_records
                
                return []
                
        except Exception as e:
            print(f"❌ Error in _fetch_real_market_data: {e}")
            return []


async def fetch_prices(
    commodity: str,
    days: int = 7,
    limit: int = 100,
    state: str = None,
    district: str = None,
) -> List[MandiPriceRow]:
    """
    Fetch commodity prices from Agmarknet API
    
    Args:
        commodity: Name of the commodity
        days: Number of days to look back
        limit: Maximum number of records to return
        state: State name (optional)
        district: District name (optional)
        
    Returns:
        List of price records
    """
    try:
        client = AgmarknetClient()
        raw_data = await client.get_market_prices(commodity, state, district)
        
        # Convert to MandiPriceRow format
        price_rows = []
        for item in raw_data[:limit]:
            try:
                price_row = MandiPriceRow(
                    market=item["mandi_name"],
                    state=item["state"],
                    district=item["district"],
                    commodity=item["commodity"],
                    variety=item.get("variety", ""),
                    min_price=item["min_price"],
                    max_price=item["max_price"],
                    modal_price=item["modal_price"],
                    arrival_date=item["date"]
                )
                price_rows.append(price_row)
            except (KeyError, ValueError) as e:
                print(f"⚠️ Skipping invalid price row: {e}")
                continue
        
        return price_rows
        
    except Exception as e:
        print(f"❌ Error in fetch_prices: {e}")
        return []


