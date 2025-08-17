"""
Soil Health Data Collection Service
Collects and processes soil health data from government sources
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class SoilHealthData:
    """Structured soil health data"""
    pincode: str
    district: str
    state: str
    soil_type: str
    ph_level: float
    organic_carbon: float
    nitrogen_n: float
    phosphorus_p: float
    potassium_k: float
    zinc_zn: float
    iron_fe: float
    manganese_mn: float
    copper_cu: float
    boron_b: float
    sulfur_s: float
    collected_date: date
    source: str
    reliability_score: float

class SoilHealthService:
    """Service for collecting and processing soil health data"""
    
    def __init__(self):
        self.base_url = "https://soilhealth.dac.gov.in"
        self.cache_duration_hours = 24
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_soil_data_by_pincode(self, pincode: str) -> Optional[SoilHealthData]:
        """
        Get soil health data for a specific pincode
        
        Args:
            pincode: 6-digit postal code
            
        Returns:
            SoilHealthData object or None if not found
        """
        try:
            logger.info(f"Fetching soil health data for pincode: {pincode}")
            
            # Try multiple data sources for comprehensive coverage
            soil_data = await self._fetch_from_soil_health_portal(pincode)
            
            if not soil_data:
                # Fallback to district-level data
                district = await self._get_district_from_pincode(pincode)
                if district:
                    soil_data = await self._fetch_district_level_data(district)
            
            if soil_data:
                # Validate and clean data
                validated_data = self._validate_soil_data(soil_data)
                if validated_data:
                    return validated_data
            
            logger.warning(f"No soil health data found for pincode: {pincode}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching soil health data for pincode {pincode}: {e}")
            return None
    
    async def _fetch_from_soil_health_portal(self, pincode: str) -> Optional[Dict[str, Any]]:
        """Fetch data from the main soil health portal"""
        try:
            # Search URL for the portal
            search_url = f"{self.base_url}/search"
            
            # Search parameters
            params = {
                'pincode': pincode,
                'search_type': 'pincode'
            }
            
            async with self.session.post(search_url, data=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return await self._parse_soil_health_html(html_content, pincode)
                
        except Exception as e:
            logger.error(f"Error fetching from soil health portal: {e}")
        
        return None
    
    async def _fetch_district_level_data(self, district: str) -> Optional[Dict[str, Any]]:
        """Fetch district-level soil health data as fallback"""
        try:
            # Use Karnataka state portal as fallback
            karnataka_url = "https://soilhealth.karnataka.gov.in"
            
            # Search for district-level data
            search_url = f"{karnataka_url}/district-data"
            params = {'district': district}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return await self._parse_karnataka_soil_html(html_content, district)
                
        except Exception as e:
            logger.error(f"Error fetching district-level data: {e}")
        
        return None
    
    async def _get_district_from_pincode(self, pincode: str) -> Optional[str]:
        """Get district name from pincode using government API"""
        try:
            # Use India Post pincode API
            pincode_url = f"https://api.postalpincode.in/pincode/{pincode}"
            
            async with self.session.get(pincode_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and data[0]['Status'] == 'Success':
                        return data[0]['PostOffice'][0]['District']
                        
        except Exception as e:
            logger.error(f"Error getting district from pincode: {e}")
        
        return None
    
    async def _parse_soil_health_html(self, html_content: str, pincode: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content from soil health portal"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract soil health data from HTML
            soil_data = {
                'pincode': pincode,
                'source': 'Soil Health Portal',
                'collected_date': datetime.now().date(),
                'reliability_score': 0.95
            }
            
            # Extract district and state
            location_elem = soup.find('div', {'class': 'location-info'})
            if location_elem:
                soil_data['district'] = self._extract_text(location_elem, 'district')
                soil_data['state'] = self._extract_text(location_elem, 'state')
            
            # Extract soil type
            soil_type_elem = soup.find('div', {'class': 'soil-type'})
            if soil_type_elem:
                soil_data['soil_type'] = soil_type_elem.get_text(strip=True)
            
            # Extract nutrient values
            nutrients = soup.find_all('div', {'class': 'nutrient-value'})
            for nutrient in nutrients:
                label = nutrient.find('span', {'class': 'label'})
                value = nutrient.find('span', {'class': 'value'})
                
                if label and value:
                    label_text = label.get_text(strip=True).lower()
                    value_text = value.get_text(strip=True)
                    
                    # Map nutrient labels to our data structure
                    if 'ph' in label_text:
                        soil_data['ph_level'] = self._parse_numeric_value(value_text)
                    elif 'organic carbon' in label_text or 'oc' in label_text:
                        soil_data['organic_carbon'] = self._parse_numeric_value(value_text)
                    elif 'nitrogen' in label_text or 'n' in label_text:
                        soil_data['nitrogen_n'] = self._parse_numeric_value(value_text)
                    elif 'phosphorus' in label_text or 'p' in label_text:
                        soil_data['phosphorus_p'] = self._parse_numeric_value(value_text)
                    elif 'potassium' in label_text or 'k' in label_text:
                        soil_data['potassium_k'] = self._parse_numeric_value(value_text)
                    elif 'zinc' in label_text or 'zn' in label_text:
                        soil_data['zinc_zn'] = self._parse_numeric_value(value_text)
                    elif 'iron' in label_text or 'fe' in label_text:
                        soil_data['iron_fe'] = self._parse_numeric_value(value_text)
                    elif 'manganese' in label_text or 'mn' in label_text:
                        soil_data['manganese_mn'] = self._parse_numeric_value(value_text)
                    elif 'copper' in label_text or 'cu' in label_text:
                        soil_data['copper_cu'] = self._parse_numeric_value(value_text)
                    elif 'boron' in label_text or 'b' in label_text:
                        soil_data['boron_b'] = self._parse_numeric_value(value_text)
                    elif 'sulfur' in label_text or 's' in label_text:
                        soil_data['sulfur_s'] = self._parse_numeric_value(value_text)
            
            return soil_data
            
        except Exception as e:
            logger.error(f"Error parsing soil health HTML: {e}")
            return None
    
    async def _parse_karnataka_soil_html(self, html_content: str, district: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content from Karnataka soil health portal"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            soil_data = {
                'district': district,
                'state': 'Karnataka',
                'source': 'Karnataka Soil Health Portal',
                'collected_date': datetime.now().date(),
                'reliability_score': 0.90
            }
            
            # Extract soil data from Karnataka portal format
            # Implementation depends on actual HTML structure
            
            return soil_data
            
        except Exception as e:
            logger.error(f"Error parsing Karnataka soil HTML: {e}")
            return None
    
    def _extract_text(self, element, field_name: str) -> str:
        """Extract text from HTML element"""
        try:
            field_elem = element.find('span', {'class': field_name})
            if field_elem:
                return field_elem.get_text(strip=True)
        except:
            pass
        return ""
    
    def _parse_numeric_value(self, value_text: str) -> float:
        """Parse numeric value from text"""
        try:
            # Remove units and extract numeric value
            numeric_match = re.search(r'(\d+\.?\d*)', value_text)
            if numeric_match:
                return float(numeric_match.group(1))
        except:
            pass
        return 0.0
    
    def _validate_soil_data(self, soil_data: Dict[str, Any]) -> Optional[SoilHealthData]:
        """Validate and clean soil health data"""
        try:
            # Check required fields
            required_fields = ['pincode', 'district', 'state']
            for field in required_fields:
                if not soil_data.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return None
            
            # Set default values for missing numeric fields
            numeric_fields = [
                'ph_level', 'organic_carbon', 'nitrogen_n', 'phosphorus_p', 
                'potassium_k', 'zinc_zn', 'iron_fe', 'manganese_mn', 
                'copper_cu', 'boron_b', 'sulfur_s'
            ]
            
            for field in numeric_fields:
                if field not in soil_data:
                    soil_data[field] = 0.0
            
            # Create SoilHealthData object
            return SoilHealthData(
                pincode=soil_data['pincode'],
                district=soil_data['district'],
                state=soil_data['state'],
                soil_type=soil_data.get('soil_type', 'Unknown'),
                ph_level=soil_data.get('ph_level', 0.0),
                organic_carbon=soil_data.get('organic_carbon', 0.0),
                nitrogen_n=soil_data.get('nitrogen_n', 0.0),
                phosphorus_p=soil_data.get('phosphorus_p', 0.0),
                potassium_k=soil_data.get('potassium_k', 0.0),
                zinc_zn=soil_data.get('zinc_zn', 0.0),
                iron_fe=soil_data.get('iron_fe', 0.0),
                manganese_mn=soil_data.get('manganese_mn', 0.0),
                copper_cu=soil_data.get('copper_cu', 0.0),
                boron_b=soil_data.get('boron_b', 0.0),
                sulfur_s=soil_data.get('sulfur_s', 0.0),
                collected_date=soil_data.get('collected_date', datetime.now().date()),
                source=soil_data.get('source', 'Unknown'),
                reliability_score=soil_data.get('reliability_score', 0.8)
            )
            
        except Exception as e:
            logger.error(f"Error validating soil data: {e}")
            return None
    
    async def get_bulk_soil_data(self, pincodes: List[str]) -> List[SoilHealthData]:
        """Get soil health data for multiple pincodes"""
        tasks = [self.get_soil_data_by_pincode(pincode) for pincode in pincodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, SoilHealthData):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in bulk data collection: {result}")
        
        return valid_results
    
    def export_to_csv(self, soil_data_list: List[SoilHealthData], filename: str):
        """Export soil health data to CSV for analysis"""
        try:
            # Convert to pandas DataFrame
            data_dicts = []
            for soil_data in soil_data_list:
                data_dicts.append({
                    'pincode': soil_data.pincode,
                    'district': soil_data.district,
                    'state': soil_data.state,
                    'soil_type': soil_data.soil_type,
                    'ph_level': soil_data.ph_level,
                    'organic_carbon': soil_data.organic_carbon,
                    'nitrogen_n': soil_data.nitrogen_n,
                    'phosphorus_p': soil_data.phosphorus_p,
                    'potassium_k': soil_data.potassium_k,
                    'zinc_zn': soil_data.zinc_zn,
                    'iron_fe': soil_data.iron_fe,
                    'manganese_mn': soil_data.manganese_mn,
                    'copper_cu': soil_data.copper_cu,
                    'boron_b': soil_data.boron_b,
                    'sulfur_s': soil_data.sulfur_s,
                    'collected_date': soil_data.collected_date,
                    'source': soil_data.source,
                    'reliability_score': soil_data.reliability_score
                })
            
            df = pd.DataFrame(data_dicts)
            df.to_csv(filename, index=False)
            logger.info(f"Exported {len(soil_data_list)} records to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")

# Example usage and testing
async def test_soil_health_service():
    """Test the soil health service"""
    async with SoilHealthService() as service:
        # Test single pincode
        soil_data = await service.get_soil_data_by_pincode("560001")
        if soil_data:
            print(f"Found soil data for {soil_data.pincode}: {soil_data.district}, {soil_data.state}")
            print(f"pH Level: {soil_data.ph_level}")
            print(f"Organic Carbon: {soil_data.organic_carbon}%")
            print(f"Nitrogen: {soil_data.nitrogen_n} kg/ha")
        
        # Test bulk data collection
        test_pincodes = ["560001", "560002", "560003"]
        bulk_data = await service.get_bulk_soil_data(test_pincodes)
        print(f"Collected data for {len(bulk_data)} pincodes")
        
        # Export to CSV
        if bulk_data:
            service.export_to_csv(bulk_data, "soil_health_data.csv")

if __name__ == "__main__":
    asyncio.run(test_soil_health_service())
