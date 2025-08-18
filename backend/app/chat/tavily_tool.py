"""
Tavily API tool for web search capabilities in the chat agent.
Provides real-time information from the web for agricultural queries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import lru_cache

from langchain_core.tools import tool
from app.config import settings

logger = logging.getLogger(__name__)


class TavilyWebSearchTool:
    """
    Tavily API tool for web search capabilities.
    Provides real-time information from the web for agricultural queries.
    """
    
    def __init__(self):
        """Initialize the Tavily tool."""
        self.cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
        # Check if Tavily is available
        try:
            from tavily import TavilyClient
            self.tavily_available = True
            self.client = None  # Will be initialized when needed
            logger.info("Tavily tool initialized successfully")
        except ImportError:
            self.tavily_available = False
            logger.warning("Tavily package not available. Install with: pip install tavily-python")
    
    def _get_tavily_client(self):
        """Get or create Tavily client."""
        if not self.tavily_available:
            return None
            
        if self.client is None:
            try:
                from tavily import TavilyClient
                
                api_key = settings.tavily_api_key
                if not api_key:
                    logger.warning("TAVILY_API_KEY not set. Web search will be disabled.")
                    return None
                
                self.client = TavilyClient(api_key=api_key)
                logger.info("Tavily client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
                return None
        
        return self.client
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_result, timestamp = self.cache[cache_key]
        return datetime.now() - timestamp < self.cache_duration
    
    def _get_cache_key(self, query: str, search_type: str = "web", **kwargs) -> str:
        """Generate cache key for search parameters."""
        # Create a hash of the search parameters
        param_str = f"{query}_{search_type}_{hash(str(sorted(kwargs.items())))}"
        return param_str
    
    async def _perform_search(
        self, 
        query: str, 
        search_type: str = "web",
        max_results: int = 5,
        include_answer: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform web search using Tavily API.
        
        Args:
            query: Search query string
            search_type: Type of search ("web", "news", "academic")
            max_results: Maximum number of results to return
            include_answer: Whether to include AI-generated answer
            **kwargs: Additional search parameters
            
        Returns:
            Search results dictionary
        """
        client = self._get_tavily_client()
        if not client:
            return {
                "error": "Tavily API not available. Please check your API key configuration.",
                "results": [],
                "fallback": True
            }
        
        try:
            # Prepare search parameters
            search_params = {
                "query": query,
                "search_depth": "basic",  # Use basic for faster results
                "include_answer": include_answer,
                "include_raw_content": False,  # Disable to reduce response size
                "include_images": False,  # Disable images for text-only responses
                "max_results": max_results,
                "search_type": search_type
            }
            
            # Add additional parameters
            search_params.update(kwargs)
            
            # Perform search
            logger.info(f"Performing Tavily search: {query} (type: {search_type})")
            result = client.search(**search_params)
            
            # Cache the result
            cache_key = self._get_cache_key(query, search_type, **kwargs)
            self.cache[cache_key] = (result, datetime.now())
            
            return result
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "fallback": True
            }
    
    def _format_search_results(self, result: Dict[str, Any], query: str, search_type: str) -> str:
        """Format search results into a readable response."""
        if result.get("error"):
            return f"Search Error: {result['error']}"
        
        if not result.get("results"):
            return f"I couldn't find any results for '{query}'. Please try rephrasing your search."
        
        # Build response
        response = f"**Web Search Results for: {query}**\n\n"
        
        # Add AI-generated answer if available
        if result.get("answer"):
            response += f"**Summary:** {result['answer']}\n\n"
        
        # Add top results
        response += "**Top Sources:**\n"
        for i, item in enumerate(result.get("results", [])[:3], 1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")[:200] + "..." if item.get("content") else "No content available"
            
            response += f"{i}. **{title}**\n"
            response += f"   {content}\n"
            response += f"   Source: {url}\n\n"
        
        # Add metadata
        if result.get("search_metadata"):
            search_time = result["search_metadata"].get("search_time", "Unknown")
            response += f"*Search performed at: {search_time}*\n"
        
        return response
    
    def _format_agricultural_results(self, result: Dict[str, Any], topic: str, location: str = None) -> str:
        """Format agricultural search results specifically."""
        if result.get("error"):
            return f"Agricultural Search Error: {result['error']}"
        
        if not result.get("results"):
            return f"I couldn't find any agricultural information about '{topic}'{f' in {location}' if location else ''}. Please try a different search term."
        
        # Build agricultural-specific response
        response = f"**Latest Agricultural Information: {topic}**\n"
        if location:
            response += f"**Location:** {location}\n"
        response += "\n"
        
        # Add AI-generated answer if available
        if result.get("answer"):
            response += f"**Key Updates:** {result['answer']}\n\n"
        
        # Add top agricultural results
        response += "**Recent Information:**\n"
        for i, item in enumerate(result.get("results", [])[:3], 1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")[:250] + "..." if item.get("content") else "No content available"
            
            response += f"{i}. **{title}**\n"
            response += f"   {content}\n"
            response += f"   Source: {url}\n\n"
        
        # Add agricultural recommendations
        response += "**Recommendations:**\n"
        response += "• Check official agricultural websites for detailed information\n"
        response += "• Contact local agricultural offices for specific guidance\n"
        response += "• Verify information with multiple sources before making decisions\n"
        
        return response
    
    def _format_market_results(self, result: Dict[str, Any], crop: str, location: str) -> str:
        """Format market price search results specifically."""
        if result.get("error"):
            return f"Market Search Error: {result['error']}"
        
        if not result.get("results"):
            return f"I couldn't find current market information for {crop} in {location}. Please try a different crop or location."
        
        # Build market-specific response
        response = f"**Current Market Information: {crop}**\n"
        response += f"**Location:** {location}\n\n"
        
        # Add AI-generated answer if available
        if result.get("answer"):
            response += f"**Market Summary:** {result['answer']}\n\n"
        
        # Add top market results
        response += "**Latest Market Updates:**\n"
        for i, item in enumerate(result.get("results", [])[:3], 1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")[:250] + "..." if item.get("content") else "No content available"
            
            response += f"{i}. **{title}**\n"
            response += f"   {content}\n"
            response += f"   Source: {url}\n\n"
        
        # Add market recommendations
        response += "**Market Recommendations:**\n"
        response += "• Check multiple mandi sources for price verification\n"
        response += "• Monitor price trends over time for better decisions\n"
        response += "• Consider transportation costs when comparing prices\n"
        response += "• Visit official market websites for real-time data\n"
        
        return response


# Create a global instance for the tools to use
_tavily_tool_instance = TavilyWebSearchTool()


@tool
async def search_web(
    query: str, 
    search_type: str = "web",
    max_results: int = 5
) -> str:
    """
    Search the web for current information on any topic.
    Use this tool when you need the latest information, news, or real-time data.
    
    Args:
        query: The search query (be specific for better results)
        search_type: Type of search - "web" for general info, "news" for current events, "academic" for research
        max_results: Maximum number of results to return (1-10)
        
    Returns:
        Comprehensive search results with sources and AI-generated summary
    """
    try:
        # Validate inputs
        if not query or len(query.strip()) < 3:
            return "Please provide a more specific search query (at least 3 characters)."
        
        if search_type not in ["web", "news", "academic"]:
            search_type = "web"
        
        if max_results < 1 or max_results > 10:
            max_results = 5
        
        # Check cache first
        cache_key = _tavily_tool_instance._get_cache_key(query, search_type, max_results=max_results)
        if _tavily_tool_instance._is_cache_valid(cache_key):
            cached_result, _ = _tavily_tool_instance.cache[cache_key]
            logger.info(f"Using cached result for query: {query}")
            return _tavily_tool_instance._format_search_results(cached_result, query, search_type)
        
        # Perform search
        result = await _tavily_tool_instance._perform_search(
            query=query,
            search_type=search_type,
            max_results=max_results,
            include_answer=True
        )
        
        return _tavily_tool_instance._format_search_results(result, query, search_type)
        
    except Exception as e:
        logger.error(f"Error in search_web tool: {e}")
        return f"I encountered an error while searching the web: {str(e)}"


@tool
async def search_agricultural_news(
    topic: str, 
    location: str = None,
    max_results: int = 5
) -> str:
    """
    Search for latest agricultural news, market updates, and farming information.
    Specifically designed for agricultural queries with focus on current information.
    
    Args:
        topic: Agricultural topic (e.g., "rice prices", "weather forecast", "government schemes")
        location: Optional location for localized results (e.g., "Karnataka", "India")
        max_results: Maximum number of results to return (1-5)
        
    Returns:
        Latest agricultural information with sources and recommendations
    """
    try:
        # Build agricultural-specific query
        if location:
            query = f"latest {topic} {location} agriculture farming 2025"
        else:
            query = f"latest {topic} agriculture farming 2025"
        
        # Focus on news and current information
        result = await _tavily_tool_instance._perform_search(
            query=query,
            search_type="news",
            max_results=max_results,
            include_answer=True,
            # Focus on agricultural domains
            include_domains=[
                "agriculture.gov.in", "icar.org.in", "farmer.gov.in", 
                "pmkisan.gov.in", "enam.gov.in", "agmarknet.gov.in"
            ]
        )
        
        return _tavily_tool_instance._format_agricultural_results(result, topic, location)
        
    except Exception as e:
        logger.error(f"Error in search_agricultural_news tool: {e}")
        return f"I encountered an error while searching for agricultural information: {str(e)}"


@tool
async def search_market_prices(
    crop: str, 
    location: str = "India",
    max_results: int = 3
) -> str:
    """
    Search for current market prices and trends for agricultural commodities.
    
    Args:
        crop: Name of the crop or commodity
        location: Location for market data (default: India)
        max_results: Maximum number of results to return (1-5)
        
    Returns:
        Current market information with price trends and recommendations
    """
    try:
        query = f"current market prices {crop} {location} mandi latest 2025"
        
        result = await _tavily_tool_instance._perform_search(
            query=query,
            search_type="news",
            max_results=max_results,
            include_answer=True,
            # Focus on market domains
            include_domains=[
                "agmarknet.gov.in", "data.gov.in", "enam.gov.in",
                "agriculture.gov.in", "farmer.gov.in"
            ]
        )
        
        return _tavily_tool_instance._format_market_results(result, crop, location)
        
    except Exception as e:
        logger.error(f"Error in search_market_prices tool: {e}")
        return f"I encountered an error while searching for market information: {str(e)}"


def get_tavily_tools() -> List:
    """Get all available Tavily tools."""
    if not _tavily_tool_instance.tavily_available:
        return []
    
    return [
        search_web,
        search_agricultural_news,
        search_market_prices
    ]
