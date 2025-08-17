"""
Agricultural Planning Agent Router
Provides API endpoints for the agricultural planning agent
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
from app.agents.agricultural_planning_agent import AgriculturalPlanningAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agricultural-agent", tags=["Agricultural Planning"])

# Initialize the agent
agent = AgriculturalPlanningAgent()

class QueryRequest(BaseModel):
    """Request model for agricultural queries"""
    query: str
    latitude: float
    longitude: float
    language: str = "en"
    crop_name: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for agricultural queries"""
    status: str
    query: str
    location: Dict[str, float]
    language: str
    response: str
    timestamp: str

@router.post("/query", response_model=QueryResponse)
async def process_agricultural_query(request: QueryRequest):
    """
    Process an agricultural query using the planning agent
    
    This endpoint allows farmers to ask questions about:
    - Weather conditions and forecasts
    - Market prices and trends
    - Crop planning recommendations
    - Risk assessment
    """
    try:
        logger.info(f"Processing agricultural query: {request.query}")
        
        # Process the query using the agent
        result = await agent.process_query(
            query=request.query,
            location={"lat": request.latitude, "lng": request.longitude},
            language=request.language
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing agricultural query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@router.get("/weather")
async def get_weather_data(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    crop_name: Optional[str] = Query(None, description="Crop name for specific analysis")
):
    """
    Get weather data for a location
    
    If crop_name is provided, returns crop-specific weather analysis.
    Otherwise, returns current weather and forecast.
    """
    try:
        weather_data = await agent.get_weather_data(latitude, longitude, crop_name)
        return weather_data
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")

@router.get("/market")
async def get_market_data(
    crop_name: str = Query(..., description="Crop/commodity name"),
    state: Optional[str] = Query(None, description="State name"),
    district: Optional[str] = Query(None, description="District name")
):
    """
    Get market data for a crop
    
    Returns current prices, trends, and market recommendations.
    """
    try:
        market_data = await agent.get_market_data(crop_name, state, district)
        return market_data
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

@router.post("/comprehensive-advice")
async def get_comprehensive_advice(request: QueryRequest):
    """
    Get comprehensive agricultural advice using both weather and market data
    
    This endpoint combines weather analysis and market analysis to provide
    comprehensive farming recommendations.
    """
    try:
        logger.info(f"Getting comprehensive advice for: {request.query}")
        
        advice = await agent.get_comprehensive_advice(
            query=request.query,
            location={"lat": request.latitude, "lng": request.longitude},
            crop_name=request.crop_name
        )
        
        if advice["status"] == "error":
            raise HTTPException(status_code=500, detail=advice["message"])
        
        return advice
        
    except Exception as e:
        logger.error(f"Error getting comprehensive advice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get comprehensive advice: {str(e)}")

@router.get("/agent-info")
async def get_agent_info():
    """
    Get information about the agricultural planning agent
    
    Returns agent capabilities, available tools, and usage instructions.
    """
    return {
        "agent_name": "Agricultural Planning Agent",
        "description": agent.get_agent_description(),
        "available_tools": [
            {
                "name": "Weather Tool",
                "description": "Provides weather data and crop-specific weather analysis",
                "functions": [
                    "get_current_weather(latitude, longitude)",
                    "get_weather_forecast(latitude, longitude, days)",
                    "analyze_crop_weather_impact(latitude, longitude, crop_name)"
                ]
            },
            {
                "name": "Market Tool",
                "description": "Provides market data and crop-specific market analysis",
                "functions": [
                    "get_current_prices(crop_name, state, district)",
                    "get_price_trends(crop_name, state, days)",
                    "get_market_recommendations(crop_name, state, district)"
                ]
            }
        ],
        "usage_instructions": """
        To get the best advice from this agent:
        
        1. **Be specific**: Mention the crop you're interested in
        2. **Include location**: Provide latitude and longitude
        3. **Ask clear questions**: "Should I plant wheat now?" or "What's the best time to sell rice?"
        4. **Consider both factors**: Ask about weather AND market conditions for comprehensive advice
        
        The agent will automatically use the appropriate tools to gather current data
        and provide you with intelligent, actionable recommendations.
        """,
        "example_queries": [
            "Should I plant wheat in my field now?",
            "What's the best time to sell my rice crop?",
            "Is it safe to plant cotton considering the weather?",
            "What crop should I grow for maximum profit this season?",
            "How will the current weather affect my wheat crop?"
        ]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for the agricultural agent"""
    return {
        "status": "healthy",
        "agent": "Agricultural Planning Agent",
        "tools_available": [
            "Weather Tool",
            "Market Tool"
        ],
        "timestamp": agent.get_agent_description()  # This will be replaced with actual timestamp
    }
