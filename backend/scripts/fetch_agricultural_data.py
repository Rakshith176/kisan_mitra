#!/usr/bin/env python3
"""
Agricultural Data Fetcher Script

This script fetches agricultural data from various government sources:
- ICAR (Indian Council of Agricultural Research)
- data.gov.in (Agmarknet, agricultural census)
- State Agricultural Universities
- Krishi Vigyan Kendras (KVKs)
- Ministry of Agriculture & Farmers Welfare

Usage:
    python fetch_agricultural_data.py --output-dir ./data/agricultural
    python fetch_agricultural_data.py --crop rice --state punjab
"""

import asyncio
import json
import logging
import os
import socket
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import aiofiles
import aiohttp
import click
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, validator

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data Models
class CropVariety(BaseModel):
    """Crop variety information"""
    name: str
    dtm_min: int = Field(..., description="Days to maturity (minimum)")
    dtm_max: int = Field(..., description="Days to maturity (maximum)")
    season: List[str] = Field(..., description="Growing seasons")
    yield_per_hectare: Optional[float] = Field(None, description="Expected yield in tons/ha")
    water_requirement: Optional[str] = Field(None, description="Water requirement category")
    soil_preferences: Optional[List[str]] = Field(None, description="Preferred soil types")
    
    @validator('dtm_max')
    def validate_dtm(cls, v, values):
        if 'dtm_min' in values and v < values['dtm_min']:
            raise ValueError('dtm_max must be greater than dtm_min')
        return v

class GrowthStage(BaseModel):
    """Crop growth stage information"""
    stage: str
    duration_days: int
    description: str
    care_requirements: Optional[Dict[str, Any]] = None
    critical_factors: Optional[List[str]] = None

class RegionalPractice(BaseModel):
    """Regional agricultural practices"""
    state: str
    district: Optional[str] = None
    crop: str
    variety: Optional[str] = None
    planting_window: List[str]
    irrigation_frequency: Optional[str] = None
    common_pests: Optional[List[str]] = None
    soil_preferences: Optional[List[str]] = None
    fertilizer_recommendations: Optional[Dict[str, Any]] = None

class CropKnowledge(BaseModel):
    """Complete crop knowledge base"""
    crop_name: str
    scientific_name: Optional[str] = None
    family: Optional[str] = None
    varieties: List[CropVariety]
    growth_stages: List[GrowthStage]
    regional_practices: List[RegionalPractice]
    pest_management: Optional[Dict[str, Any]] = None
    disease_management: Optional[Dict[str, Any]] = None
    harvesting_guidelines: Optional[Dict[str, Any]] = None
    storage_recommendations: Optional[Dict[str, Any]] = None
    source: str
    last_updated: datetime
    data_quality_score: Optional[float] = Field(None, ge=0, le=1)

class AgriculturalDataCollector:
    """Main data collection class"""
    
    def __init__(self, output_dir: str = "./data/agricultural"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session: Optional[aiohttp.ClientSession] = None
        self.collected_data: Dict[str, Any] = {}
        
        # API endpoints and configurations
        self.endpoints = {
            "icar": {
                "base_url": "https://icar.gov.in",
                "crop_calendar": "/api/crop-calendar",
                "varieties": "/api/crop-varieties",
                "practices": "/api/best-practices"
            },
            "data_gov_in": {
                "base_url": "https://api.data.gov.in",
                "agmarknet": "/resource/9ef84268-d588-465a-a308-a864a43d0070",
                "agricultural_census": "/resource/6eece85f-0c1b-4f0c-9cd9-31cc872d0f31",
                "soil_health": "/resource/6eece85f-0c1b-4f0c-9cd9-31cc872d0f32"
            },
            "state_universities": {
                # "punjab": {
                #     "name": "Punjab Agricultural University",
                #     "base_url": "https://www.pau.edu",
                #     "crop_info": "/research/crop-sciences",
                #     "api_base": "https://api.pau.edu"
                # },
                # "tamil_nadu": {
                #     "name": "Tamil Nadu Agricultural University", 
                #     "base_url": "https://tnau.ac.in",
                #     "crop_info": "/research/crop-sciences",
                #     "api_base": "https://api.tnau.ac.in"
                # },
                "karnataka": {
                    "name": "University of Agricultural Sciences",
                    "base_url": "https://uasbangalore.edu.in",
                    "crop_info": "/research/crop-sciences",
                    "api_base": "https://api.uasbangalore.edu.in"
                }
            },
            "kvk": {
                "base_url": "https://kvk.icar.gov.in",
                "directory": "/api/kvk-directory",
                "recommendations": "/api/recommendations"
            },
            "ministry": {
                "base_url": "https://agriculture.gov.in",
                "schemes": "/api/schemes",
                "advisories": "/api/advisories",
                "crop_calendar": "/api/crop-calendar"
            }
        }
        
        # Headers to mimic browser requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Create SSL context that's more permissive for government sites
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with SSL context and DNS settings
        connector = aiohttp.TCPConnector(
            limit=10, 
            limit_per_host=5,
            ssl=ssl_context,
            use_dns_cache=True,
            ttl_dns_cache=300,
            family=socket.AF_INET  # Force IPv4 to avoid IPv6 issues
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self.headers,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_with_retry(self, url: str, max_retries: int = 3, delay: float = 1.0) -> Optional[Dict[str, Any]]:
        """Fetch data with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Add additional headers for problematic sites
                headers = self.headers.copy()
                headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                async with self.session.get(url, headers=headers, ssl=False) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'application/json' in content_type:
                            return await response.json()
                        else:
                            # Try to parse HTML or other content
                            text = await response.text()
                            return {"raw_content": text, "content_type": content_type}
                    elif response.status == 429:
                        # Rate limited, wait longer
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Connection error on attempt {attempt + 1} for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                    continue
                else:
                    logger.error(f"All connection attempts failed for {url}")
                    
            except aiohttp.ClientSSLError as e:
                logger.error(f"SSL error on attempt {attempt + 1} for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                    continue
                else:
                    logger.error(f"All SSL attempts failed for {url}")
                    
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1} for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                    continue
                else:
                    logger.error(f"All retries failed for {url}")
                    
        return None

    async def fetch_icar_data(self) -> Dict[str, Any]:
        """Fetch data from ICAR (Indian Council of Agricultural Research)"""
        logger.info("Fetching data from ICAR...")
        icar_data = {}
        
        try:
            # Fetch crop calendar
            calendar_url = urljoin(self.endpoints["icar"]["base_url"], self.endpoints["icar"]["crop_calendar"])
            calendar_data = await self.fetch_with_retry(calendar_url)
            if calendar_data:
                icar_data["crop_calendar"] = calendar_data
                logger.info("✓ Fetched ICAR crop calendar")
            
            # Fetch crop varieties
            varieties_url = urljoin(self.endpoints["icar"]["base_url"], self.endpoints["icar"]["varieties"])
            varieties_data = await self.fetch_with_retry(varieties_url)
            if varieties_data:
                icar_data["crop_varieties"] = varieties_data
                logger.info("✓ Fetched ICAR crop varieties")
            
            # Fetch best practices
            practices_url = urljoin(self.endpoints["icar"]["base_url"], self.endpoints["icar"]["practices"])
            practices_data = await self.fetch_with_retry(practices_url)
            if practices_data:
                icar_data["best_practices"] = practices_data
                logger.info("✓ Fetched ICAR best practices")
                
        except Exception as e:
            logger.error(f"Error fetching ICAR data: {e}")
            
        return icar_data

    async def fetch_data_gov_in_data(self) -> Dict[str, Any]:
        """Fetch data from data.gov.in APIs"""
        logger.info("Fetching data from data.gov.in...")
        gov_data = {}
        
        try:
            # Fetch Agmarknet data (market prices)
            if hasattr(settings, 'data_gov_in_api_key') and settings.data_gov_in_api_key:
                agmarknet_url = f"{self.endpoints['data_gov_in']['base_url']}{self.endpoints['data_gov_in']['agmarknet']}"
                params = {
                    "api-key": settings.data_gov_in_api_key,
                    "format": "json",
                    "limit": 1000
                }
                
                async with self.session.get(agmarknet_url, params=params) as response:
                    if response.status == 200:
                        gov_data["agmarknet"] = await response.json()
                        logger.info("✓ Fetched Agmarknet data")
                    else:
                        logger.warning(f"Failed to fetch Agmarknet data: HTTP {response.status}")
            
            # Fetch agricultural census data
            census_url = f"{self.endpoints['data_gov_in']['base_url']}{self.endpoints['data_gov_in']['agricultural_census']}"
            census_data = await self.fetch_with_retry(census_url)
            if census_data:
                gov_data["agricultural_census"] = census_data
                logger.info("✓ Fetched agricultural census data")
                
        except Exception as e:
            logger.error(f"Error fetching data.gov.in data: {e}")
            
        return gov_data

    async def fetch_state_university_data(self) -> Dict[str, Any]:
        """Fetch data from state agricultural universities"""
        logger.info("Fetching data from state agricultural universities...")
        university_data = {}
        
        for state, config in self.endpoints["state_universities"].items():
            try:
                logger.info(f"Fetching from {config['name']}...")
                
                # Try to fetch crop information
                crop_url = urljoin(config["base_url"], config["crop_info"])
                crop_data = await self.fetch_with_retry(crop_url)
                
                if crop_data:
                    university_data[state] = {
                        "university_name": config["name"],
                        "crop_information": crop_data,
                        "source_url": crop_url,
                        "fetched_at": datetime.utcnow().isoformat()
                    }
                    logger.info(f"✓ Fetched data from {config['name']}")
                else:
                    logger.warning(f"No data fetched from {config['name']}")
                    
            except Exception as e:
                logger.error(f"Error fetching from {config['name']}: {e}")
                
        return university_data

    async def test_connectivity(self, url: str) -> bool:
        """Test basic connectivity to a URL"""
        try:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            # Test DNS resolution
            try:
                ip = socket.gethostbyname(host)
                logger.info(f"✓ DNS resolution successful for {host}: {ip}")
            except socket.gaierror as e:
                logger.error(f"✗ DNS resolution failed for {host}: {e}")
                return False
            
            # Test basic connectivity
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    logger.info(f"✓ Basic connectivity successful for {host}:{port}")
                    return True
                else:
                    logger.error(f"✗ Basic connectivity failed for {host}:{port} (error code: {result})")
                    return False
            except Exception as e:
                logger.error(f"✗ Socket test failed for {host}:{port}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Connectivity test failed for {url}: {e}")
            return False

    async def fetch_kvk_data(self) -> Dict[str, Any]:
        """Fetch data from Krishi Vigyan Kendras (KVKs)"""
        logger.info("Fetching data from KVKs...")
        kvk_data = {}
        
        try:
            # Test connectivity first
            base_url = self.endpoints["kvk"]["base_url"]
            if not await self.test_connectivity(base_url):
                logger.warning(f"Skipping KVK data collection due to connectivity issues with {base_url}")
                return {"error": "Connectivity test failed", "base_url": base_url}
            
            # Fetch KVK directory
            directory_url = urljoin(base_url, self.endpoints["kvk"]["directory"])
            directory_data = await self.fetch_with_retry(directory_url)
            if directory_data:
                kvk_data["kvk_directory"] = directory_data
                logger.info("✓ Fetched KVK directory")
            
            # Fetch recommendations
            recommendations_url = urljoin(base_url, self.endpoints["kvk"]["recommendations"])
            recommendations_data = await self.fetch_with_retry(recommendations_url)
            if recommendations_data:
                kvk_data["recommendations"] = recommendations_data
                logger.info("✓ Fetched KVK recommendations")
                
        except Exception as e:
            logger.error(f"Error fetching KVK data: {e}")
            
        return kvk_data

    async def fetch_ministry_data(self) -> Dict[str, Any]:
        """Fetch data from Ministry of Agriculture & Farmers Welfare"""
        logger.info("Fetching data from Ministry of Agriculture...")
        ministry_data = {}
        
        try:
            # Fetch schemes
            schemes_url = urljoin(self.endpoints["ministry"]["base_url"], self.endpoints["ministry"]["schemes"])
            schemes_data = await self.fetch_with_retry(schemes_url)
            if schemes_data:
                ministry_data["schemes"] = schemes_data
                logger.info("✓ Fetched agricultural schemes")
            
            # Fetch advisories
            advisories_url = urljoin(self.endpoints["ministry"]["base_url"], self.endpoints["ministry"]["advisories"])
            advisories_data = await self.fetch_with_retry(advisories_url)
            if advisories_data:
                ministry_data["advisories"] = advisories_data
                logger.info("✓ Fetched agricultural advisories")
                
        except Exception as e:
            logger.error(f"Error fetching ministry data: {e}")
            
        return ministry_data

    async def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch data from all sources"""
        logger.info("Starting comprehensive agricultural data collection...")
        
        # Check which sources to skip
        sources_to_fetch = []
        source_names = []
        
        if not self.endpoints.get("icar", {}).get("_skip", False):
            sources_to_fetch.append(self.fetch_icar_data())
            source_names.append("icar")
        
        if not self.endpoints.get("data_gov_in", {}).get("_skip", False):
            sources_to_fetch.append(self.fetch_data_gov_in_data())
            source_names.append("data_gov_in")
        
        if not self.endpoints.get("state_universities", {}).get("_skip", False):
            sources_to_fetch.append(self.fetch_state_university_data())
            source_names.append("state_universities")
        
        if not self.endpoints.get("kvk", {}).get("_skip", False):
            sources_to_fetch.append(self.fetch_kvk_data())
            source_names.append("kvk")
        
        if not self.endpoints.get("ministry", {}).get("_skip", False):
            sources_to_fetch.append(self.fetch_ministry_data())
            source_names.append("ministry")
        
        if not sources_to_fetch:
            logger.warning("All sources marked as problematic, no data will be fetched")
            return {
                "metadata": {
                    "collection_timestamp": datetime.utcnow().isoformat(),
                    "script_version": "1.0.0",
                    "data_sources": [],
                    "total_sources": 0,
                    "note": "All sources skipped due to connectivity issues"
                }
            }
        
        # Fetch from available sources concurrently
        results = await asyncio.gather(*sources_to_fetch, return_exceptions=True)
        
        # Combine results
        all_data = {
            "metadata": {
                "collection_timestamp": datetime.utcnow().isoformat(),
                "script_version": "1.0.0",
                "data_sources": source_names,
                "total_sources": len(source_names)
            }
        }
        
        # Add results for each source
        for i, source_name in enumerate(source_names):
            all_data[source_name] = results[i] if not isinstance(results[i], Exception) else {"error": str(results[i])}
        
        # Calculate success rate
        successful_sources = sum(1 for r in results if not isinstance(r, Exception))
        all_data["metadata"]["success_rate"] = f"{successful_sources}/{len(results)}"
        
        logger.info(f"Data collection completed. Success rate: {successful_sources}/{len(results)}")
        return all_data

    async def save_data(self, data: Dict[str, Any], filename: str = None) -> str:
        """Save collected data to JSON file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"agricultural_data_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
            
            logger.info(f"✓ Data saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

    async def generate_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate a summary report of collected data"""
        report = []
        report.append("=" * 80)
        report.append("AGRICULTURAL DATA COLLECTION SUMMARY REPORT")
        report.append("=" * 80)
        report.append(f"Collection Date: {data['metadata']['collection_timestamp']}")
        report.append(f"Script Version: {data['metadata']['script_version']}")
        report.append(f"Success Rate: {data['metadata']['success_rate']}")
        report.append("")
        
        for source, source_data in data.items():
            if source == "metadata":
                continue
                
            report.append(f"📊 {source.upper().replace('_', ' ')}")
            report.append("-" * 40)
            
            if isinstance(source_data, dict) and "error" in source_data:
                report.append(f"❌ Error: {source_data['error']}")
            elif source_data:
                report.append(f"✅ Data collected successfully")
                if isinstance(source_data, dict):
                    for key, value in source_data.items():
                        if isinstance(value, (list, dict)):
                            report.append(f"   • {key}: {len(value)} items")
                        else:
                            report.append(f"   • {key}: {value}")
            else:
                report.append("⚠️  No data collected")
            
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)

@click.command()
@click.option('--output-dir', default='./data/agricultural', help='Output directory for JSON files')
@click.option('--crop', help='Filter data for specific crop')
@click.option('--state', help='Filter data for specific state')
@click.option('--generate-report', is_flag=True, help='Generate summary report')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
@click.option('--skip-ssl-verify', is_flag=True, help='Skip SSL verification for problematic sites')
@click.option('--test-connectivity', is_flag=True, help='Test connectivity to all sources before fetching')
@click.option('--skip-problematic', is_flag=True, help='Skip sources with connectivity issues')
def main(output_dir: str, crop: str, state: str, generate_report: bool, verbose: bool, 
         skip_ssl_verify: bool, test_connectivity: bool, skip_problematic: bool):
    """Fetch agricultural data from government sources"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async def run():
        async with AgriculturalDataCollector(output_dir) as collector:
            # Test connectivity first if requested
            if test_connectivity:
                logger.info("Testing connectivity to all data sources...")
                for source_name, source_config in collector.endpoints.items():
                    if isinstance(source_config, dict) and 'base_url' in source_config:
                        is_accessible = await collector.test_connectivity(source_config['base_url'])
                        if not is_accessible and skip_problematic:
                            logger.warning(f"Skipping {source_name} due to connectivity issues")
                            # Mark this source as problematic
                            collector.endpoints[source_name]['_skip'] = True
            
            # Fetch all data
            data = await collector.fetch_all_data()
            
            # Apply filters if specified
            if crop or state:
                data = filter_data(data, crop, state)
            
            # Save data
            filename = f"agricultural_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            if crop:
                filename = f"agricultural_data_{crop}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            if state:
                filename = f"agricultural_data_{state}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = await collector.save_data(data, filename)
            
            # Generate report if requested
            if generate_report:
                report = await collector.generate_summary_report(data)
                report_file = Path(output_dir) / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
                async with aiofiles.open(report_file, 'w', encoding='utf-8') as f:
                    await f.write(report)
                print(f"\n📋 Summary report saved to: {report_file}")
            
            print(f"\n✅ Agricultural data collection completed!")
            print(f"📁 Data saved to: {filepath}")
            print(f"📊 Success rate: {data['metadata']['success_rate']}")
    
    asyncio.run(run())

def filter_data(data: Dict[str, Any], crop: str = None, state: str = None) -> Dict[str, Any]:
    """Filter collected data based on crop and state parameters"""
    if not crop and not state:
        return data
    
    filtered_data = {"metadata": data["metadata"], "filters_applied": {"crop": crop, "state": state}}
    
    # Apply filters to each source
    for source, source_data in data.items():
        if source == "metadata":
            continue
            
        if isinstance(source_data, dict) and "error" not in source_data:
            # Simple filtering logic - can be enhanced based on actual data structure
            filtered_data[source] = source_data
    
    return filtered_data

if __name__ == "__main__":
    main()
