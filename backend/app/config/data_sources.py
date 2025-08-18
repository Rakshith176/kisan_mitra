"""
Data Sources Configuration
Configuration for all external data sources used in the crop planning module
"""

from typing import Dict, Any
from pydantic import BaseSettings

class DataSourceSettings(BaseSettings):
    """Configuration for external data sources"""
    
    # Weather Data Sources
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_TIMEOUT: int = 20
    OPEN_METEO_CACHE_DURATION_HOURS: int = 6
    
    # Market Data Sources
    AGMARKNET_BASE_URL: str = "https://agmarknet.gov.in/api/v1"
    AGMARKNET_TIMEOUT: int = 30
    AGMARKNET_CACHE_DURATION_HOURS: int = 12
    
    # Soil Health Data Sources
    SOIL_HEALTH_PORTAL_URL: str = "https://soilhealth.dac.gov.in"
    KARNATAKA_SOIL_URL: str = "https://soilhealth.karnataka.gov.in"
    SOIL_DATA_CACHE_DURATION_HOURS: int = 24
    
    # Crop Calendar Data Sources
    ICAR_BASE_URL: str = "https://icar.org.in"
    KARNATAKA_AGRI_URL: str = "https://raitamitra.karnataka.gov.in"
    CROP_CALENDAR_CACHE_DURATION_HOURS: int = 168  # 1 week
    
    # Government Scheme Data Sources
    SCHEME_DATABASE_URL: str = "https://pmkisan.gov.in"
    SCHEME_CACHE_DURATION_HOURS: int = 24
    
    # Data Collection Settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5
    BATCH_SIZE: int = 100
    MAX_CONCURRENT_REQUESTS: int = 10
    
    # Cache Settings
    DEFAULT_CACHE_DURATION_HOURS: int = 6
    MAX_CACHE_SIZE: int = 1000
    CACHE_CLEANUP_INTERVAL_HOURS: int = 24
    
    # API Rate Limiting
    WEATHER_API_RATE_LIMIT: int = 100  # requests per hour
    MARKET_API_RATE_LIMIT: int = 50    # requests per hour
    SOIL_API_RATE_LIMIT: int = 200     # requests per hour
    
    # Data Quality Settings
    MIN_DATA_RELIABILITY_SCORE: float = 0.7
    MAX_DATA_AGE_DAYS: int = 30
    REQUIRED_FIELDS_THRESHOLD: float = 0.8
    
    # Fallback Data Settings
    ENABLE_FALLBACK_DATA: bool = True
    FALLBACK_DATA_RELIABILITY: float = 0.5
    FALLBACK_DATA_MAX_AGE_DAYS: int = 90
    
    # Monitoring Settings
    ENABLE_DATA_SOURCE_MONITORING: bool = True
    MONITORING_INTERVAL_MINUTES: int = 15
    ALERT_THRESHOLD_ERROR_RATE: float = 0.1
    
    class Config:
        env_file = ".env"
        env_prefix = "DATA_SOURCE_"

# Data source endpoints
WEATHER_ENDPOINTS = {
    "current_weather": "/forecast",
    "weather_forecast": "/forecast",
    "historical_weather": "/forecast"
}

MARKET_ENDPOINTS = {
    "current_prices": "/market-prices",
    "price_history": "/price-history",
    "market_list": "/markets"
}

SOIL_ENDPOINTS = {
    "soil_health": "/search",
    "nutrient_data": "/nutrients",
    "soil_type": "/soil-types"
}

CROP_CALENDAR_ENDPOINTS = {
    "crop_calendar": "/crop-calendar",
    "growth_stages": "/growth-stages",
    "seasonal_data": "/seasonal-data"
}

# Data source headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Data source timeouts
TIMEOUTS = {
    "weather": 20,
    "market": 30,
    "soil": 25,
    "crop_calendar": 30,
    "schemes": 20
}

# Data validation rules
VALIDATION_RULES = {
    "weather": {
        "temperature_range": (-50, 60),
        "humidity_range": (0, 100),
        "rainfall_range": (0, 1000),
        "wind_speed_range": (0, 200)
    },
    "market": {
        "price_range": (0, 100000),
        "date_format": "%Y-%m-%d",
        "required_fields": ["mandi_name", "modal_price", "date"]
    },
    "soil": {
        "ph_range": (0, 14),
        "nutrient_range": (0, 10000),
        "organic_carbon_range": (0, 10),
        "required_fields": ["pincode", "ph_level", "soil_type"]
    }
}

# Error handling configuration
ERROR_HANDLING = {
    "max_retries": 3,
    "retry_delay": 5,
    "exponential_backoff": True,
    "circuit_breaker_threshold": 5,
    "circuit_breaker_timeout": 300
}

# Data source priorities (for fallback)
DATA_SOURCE_PRIORITIES = {
    "weather": ["open_meteo", "weather_tool", "fallback"],
    "market": ["agmarknet", "market_tool", "fallback"],
    "soil": ["soil_health_portal", "karnataka_portal", "fallback"],
    "crop_calendar": ["icar", "state_portals", "fallback"]
}

# Data quality thresholds
QUALITY_THRESHOLDS = {
    "excellent": 0.9,
    "good": 0.7,
    "acceptable": 0.5,
    "poor": 0.3
}

# Cache invalidation triggers
CACHE_INVALIDATION_TRIGGERS = {
    "weather": ["temperature_change_5c", "rainfall_change_10mm", "time_6h"],
    "market": ["price_change_10pct", "new_data_available", "time_12h"],
    "soil": ["new_test_results", "seasonal_changes", "time_24h"],
    "crop_calendar": ["seasonal_updates", "new_varieties", "time_168h"]
}

# Data source health check endpoints
HEALTH_CHECK_ENDPOINTS = {
    "open_meteo": "https://api.open-meteo.com/v1/health",
    "agmarknet": "https://agmarknet.gov.in/api/v1/health",
    "soil_health": "https://soilhealth.dac.gov.in/health",
    "icar": "https://icar.org.in/health"
}

# Data source rate limiting configuration
RATE_LIMITING = {
    "open_meteo": {
        "requests_per_hour": 100,
        "burst_limit": 20,
        "window_size": 3600
    },
    "agmarknet": {
        "requests_per_hour": 50,
        "burst_limit": 10,
        "window_size": 3600
    },
    "soil_health": {
        "requests_per_hour": 200,
        "burst_limit": 50,
        "window_size": 3600
    }
}

# Data source fallback configuration
FALLBACK_CONFIG = {
    "weather": {
        "enabled": True,
        "data_age_limit_hours": 24,
        "reliability_threshold": 0.5
    },
    "market": {
        "enabled": True,
        "data_age_limit_hours": 48,
        "reliability_threshold": 0.6
    },
    "soil": {
        "enabled": True,
        "data_age_limit_hours": 168,
        "reliability_threshold": 0.7
    }
}

# Data source monitoring configuration
MONITORING_CONFIG = {
    "enabled": True,
    "metrics": ["response_time", "success_rate", "data_quality", "cache_hit_rate"],
    "alerts": {
        "high_error_rate": 0.1,
        "slow_response_time": 5000,
        "low_data_quality": 0.5,
        "cache_miss_rate": 0.3
    },
    "reporting_interval_minutes": 15
}

# Export the settings
data_source_settings = DataSourceSettings()
