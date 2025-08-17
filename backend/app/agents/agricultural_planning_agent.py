"""
Agricultural Planning Agent
Uses weather and market tools to provide intelligent crop planning advice
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from app.services.weather_tool import WeatherTool
from app.services.market_tool import MarketTool
from app.config import settings

logger = logging.getLogger(__name__)

class AgriculturalPlanningAgent:
    """Agent that provides intelligent agricultural planning using weather and market data"""
    
    def __init__(self):
        self.weather_tool = WeatherTool()
        self.market_tool = MarketTool()
        
        # Initialize Gemini
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        # Agent prompt template
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agricultural planning agent"""
        return """
        You are an expert Agricultural Planning Agent with access to real-time weather data and market information. Your role is to help farmers make informed decisions about crop planning, planting, and market timing.

        ## YOUR CAPABILITIES:
        You have access to two powerful tools:

        ### 1. WEATHER TOOL
        - Current weather conditions for any location
        - 7-14 day weather forecasts
        - Crop-specific weather impact analysis
        - Weather risk assessment and recommendations

        ### 2. MARKET TOOL
        - Current market prices for crops across India
        - Price trends and market analysis
        - Market recommendations for selling crops
        - Price comparison across different markets

        ## YOUR APPROACH:
        1. **ALWAYS USE TOOLS FIRST**: When a farmer asks a question, immediately use the appropriate tools to gather current data
        2. **MULTIPLE TOOL CALLS**: Don't hesitate to call tools multiple times if you need more information
        3. **COMBINE DATA**: Synthesize weather and market data to provide comprehensive advice
        4. **BE SPECIFIC**: Provide actionable, location-specific recommendations
        5. **EXPLAIN REASONING**: Always explain why you're recommending something

        ## TOOL USAGE STRATEGY:
        - **For weather questions**: Use weather tools to get current conditions and forecasts
        - **For market questions**: Use market tools to get prices and trends
        - **For crop planning**: Use BOTH tools to provide weather-safe, market-optimized advice
        - **For complex questions**: Use tools multiple times to gather comprehensive information

        ## RESPONSE FORMAT:
        Always structure your responses with:
        1. **Data Summary**: Brief summary of what you found from tools
        2. **Analysis**: Your interpretation of the data
        3. **Recommendations**: Specific, actionable advice
        4. **Reasoning**: Why you're making these recommendations
        5. **Next Steps**: What the farmer should do next

        ## IMPORTANT RULES:
        - NEVER make up weather or market data - always use tools
        - If you need more information, call tools again
        - Be conservative with recommendations - farming involves real risks
        - Consider both weather safety and market profitability
        - Provide advice in simple, clear language
        - Always mention any risks or uncertainties

        ## EXAMPLE WORKFLOW:
        When asked "Should I plant wheat in Punjab now?":
        1. Use weather tool to check current conditions and forecast
        2. Use market tool to check wheat prices and trends
        3. Combine both datasets to assess planting timing
        4. Provide specific recommendation with reasoning
        5. Suggest monitoring and next steps

        Remember: You are a trusted agricultural advisor. Your recommendations can significantly impact a farmer's livelihood, so be thorough, accurate, and helpful.
        """
    
    async def process_query(self, query: str, location: Dict[str, float], language: str = "en") -> Dict[str, Any]:
        """
        Process a farmer's query and provide intelligent agricultural advice
        
        Args:
            query: The farmer's question
            location: Dictionary with 'lat' and 'lng' coordinates
            language: Language preference (en/hi/kn)
            
        Returns:
            Comprehensive agricultural advice
        """
        try:
            logger.info(f"Processing agricultural query: {query}")
            
            # Create the user prompt with context
            user_prompt = f"""
            Farmer's Question: {query}
            
            Location: Latitude {location['lat']}, Longitude {location['lng']}
            Language: {language}
            
            Please provide comprehensive agricultural advice using the available tools.
            """
            
            # Create the full prompt for the LLM
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            # Get LLM response with tool usage instructions
            response = await self._get_llm_response(full_prompt, query, location)
            
            return {
                "status": "success",
                "query": query,
                "location": location,
                "language": language,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing agricultural query: {e}")
            return {
                "status": "error",
                "message": f"Failed to process query: {str(e)}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_llm_response(self, prompt: str, query: str, location: Dict[str, float]) -> str:
        """
        Get LLM response with tool usage guidance
        
        Args:
            prompt: The full system prompt
            query: The farmer's question
            location: Location coordinates
            
        Returns:
            LLM response with tool usage instructions
        """
        try:
            # Generate initial response
            response = self.model.generate_content(prompt)
            
            # Extract the response text
            response_text = response.text
            
            # Add tool usage guidance if the LLM hasn't used tools
            if "tool" not in response_text.lower() and "weather" not in response_text.lower() and "market" not in response_text.lower():
                response_text += f"""

## 🔧 TOOL USAGE REQUIRED

I notice I haven't used the available tools yet. Let me gather the necessary data to provide you with accurate advice.

**For your question: "{query}"**

I need to use the following tools:
1. **Weather Tool** - To check current conditions and forecast for your location
2. **Market Tool** - To analyze current prices and market trends

**Please ask me to use these tools specifically, or rephrase your question to include:**
- What crop you're interested in
- Whether you want weather analysis, market analysis, or both
- Any specific timeframes you're considering

Example: "Check the weather and market conditions for wheat in my area" or "What's the best time to plant rice considering weather and prices?"
"""
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return f"Error generating response: {str(e)}"
    
    async def get_weather_data(self, latitude: float, longitude: float, crop_name: str = None) -> Dict[str, Any]:
        """Get weather data using the weather tool"""
        if crop_name:
            return await self.weather_tool.analyze_crop_weather_impact(latitude, longitude, crop_name)
        else:
            current = await self.weather_tool.get_current_weather(latitude, longitude)
            forecast = await self.weather_tool.get_weather_forecast(latitude, longitude, 7)
            return {
                "current_weather": current,
                "weather_forecast": forecast
            }
    
    async def get_market_data(self, crop_name: str, state: str = None, district: str = None) -> Dict[str, Any]:
        """Get market data using the market tool"""
        prices = await self.market_tool.get_current_prices(crop_name, state, district)
        trends = await self.market_tool.get_price_trends(crop_name, state, 30)
        recommendations = await self.market_tool.get_market_recommendations(crop_name, state, district)
        
        return {
            "current_prices": prices,
            "price_trends": trends,
            "market_recommendations": recommendations
        }
    
    async def get_comprehensive_advice(self, query: str, location: Dict[str, float], crop_name: str = None) -> Dict[str, Any]:
        """
        Get comprehensive advice using both weather and market tools
        
        Args:
            query: The farmer's question
            location: Location coordinates
            crop_name: Optional crop name for specific analysis
            
        Returns:
            Comprehensive agricultural advice
        """
        try:
            # Gather weather data
            weather_data = await self.get_weather_data(location['lat'], location['lng'], crop_name)
            
            # Gather market data if crop is specified
            market_data = None
            if crop_name:
                market_data = await self.get_market_data(crop_name)
            
            # Create comprehensive analysis prompt
            analysis_prompt = f"""
            Based on the following data, provide comprehensive agricultural advice:

            WEATHER DATA:
            {json.dumps(weather_data, indent=2)}

            MARKET DATA:
            {json.dumps(market_data, indent=2) if market_data else "No market data available"}

            FARMER'S QUESTION: {query}
            LOCATION: {location}

            Please provide:
            1. Summary of current conditions
            2. Analysis of weather and market factors
            3. Specific recommendations
            4. Risk assessment
            5. Next steps and monitoring advice
            """
            
            # Get LLM analysis
            response = self.model.generate_content(analysis_prompt)
            
            return {
                "status": "success",
                "weather_data": weather_data,
                "market_data": market_data,
                "analysis": response.text,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive advice: {e}")
            return {
                "status": "error",
                "message": f"Failed to get comprehensive advice: {str(e)}"
            }
    
    def get_agent_description(self) -> str:
        """Get agent description for documentation"""
        return """
        Agricultural Planning Agent
        
        This agent provides intelligent agricultural advice by combining:
        - Real-time weather data and forecasts
        - Current market prices and trends
        - Crop-specific analysis and recommendations
        
        The agent can:
        - Analyze weather conditions for crop planning
        - Assess market conditions for selling decisions
        - Provide comprehensive farming recommendations
        - Consider both weather safety and market profitability
        
        Available tools:
        1. Weather Tool - For weather analysis and crop impact assessment
        2. Market Tool - For price analysis and market recommendations
        
        The agent is designed to use tools multiple times when needed to provide comprehensive, accurate advice.
        """
