"""
Chat agent using LangChain with Gemini for multimodal conversations.
"""

import asyncio
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.rag.rag_service import RAGService
from app.chat.govt_schemes_tool import GovernmentSchemesTool
from app.chat.weather_tool import WeatherTool
from app.chat.tavily_tool import get_tavily_tools
from app.chat.schemas import ChatRequest, ChatResponse, ConversationContext, MediaType, ChatMessage

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    LangChain-based chat agent using Gemini for multimodal conversations.
    Supports text, image, and audio inputs with text and audio outputs.
    """
    
    def __init__(self):
        """Initialize the chat agent with LangChain and Gemini configuration."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        try:
            # Initialize LangChain Gemini model
            self.llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.7,
                convert_system_message_to_human=True
            )
            
            # Check if the model supports vision
            if "gemini-2.5-flash" in settings.gemini_model.lower():
                self.supports_vision = True
                logger.info(f"Chat agent initialized with vision-capable model: {settings.gemini_model}")
            else:
                self.supports_vision = False
                logger.warning(f"Model {settings.gemini_model} may not support vision. Image processing may fail.")
            
            # Initialize RAG service
            self.rag_service = RAGService()
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain Gemini model: {e}")
            raise ValueError(f"LangChain Gemini model initialization failed: {e}")
        
        self.chat_sessions: Dict[str, List] = {}
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info("LangChain chat agent initialized successfully")
    
    def _create_tools(self) -> List:
        """Create LangChain tools for the agent."""
        
        @tool
        async def get_crop_information(query: str, user_crops: List[str] = None, current_season: str = None) -> str:
            """
            Get detailed agricultural information from RAG system.
            
            Args:
                query: The agricultural question or topic
                user_crops: List of crops the user is interested in
                current_season: Current agricultural season (kharif, rabi, zaid)
                
            Returns:
                Detailed agricultural information and recommendations
            """
            try:
                from app.rag.models import QueryContext
                
                # Create query context
                context = QueryContext(
                    query=query,
                    user_crops=user_crops or [],
                    current_season=current_season,
                    language="en"  # Default to English for RAG queries
                )
                
                # Query RAG system
                result = await self.rag_service.query(query, context)
                return result
                if result.get('chunks'):
                    # Check if this is a government scheme query
                    is_scheme_query = any(keyword in query.lower() for keyword in [
                        'scheme', 'pm kisan', 'pmksy', 'pmfby', 'enam', 'kcc', 'fpo',
                        'budget', 'allocation', 'eligibility', 'benefit', 'application',
                        'government', 'policy', 'subsidy', 'loan', 'insurance'
                    ])
                    
                    if is_scheme_query:
                        # Enhanced response for government scheme queries
                        response = f"**Government Scheme Information**\n\n"
                        
                        # Extract scheme-specific information
                        schemes = set()
                        budgets = []
                        beneficiaries = set()
                        eligibility = []
                        
                        for chunk in result['chunks'][:3]:  # Top 3 chunks
                            metadata = chunk.get('metadata', {})
                            
                            if metadata.get('scheme_name'):
                                schemes.update(metadata['scheme_name'])
                            if metadata.get('budget_amount') and metadata.get('budget_unit'):
                                budgets.append(f"{metadata['budget_amount']} {metadata['budget_unit']}")
                            if metadata.get('eligibility_criteria'):
                                eligibility.extend(metadata['eligibility_criteria'])
                        
                        # Build comprehensive response
                        if schemes:
                            response += f"**Relevant Schemes:** {', '.join(schemes)}\n\n"
                        if budgets:
                            response += f"**Budget Allocations:** {', '.join(budgets)}\n\n"
                        if beneficiaries:
                            response += f"**Target Beneficiaries:** {', '.join(beneficiaries)}\n\n"
                        if eligibility:
                            response += f"**Eligibility Criteria:** {', '.join(eligibility[:3])}\n\n"
                        
                        # Add chunk content
                        for i, chunk in enumerate(result['chunks'][:2], 1):
                            response += f"**Details {i}:** {chunk.get('content', '')[:300]}...\n\n"
                        
                        if result.get('summary'):
                            response += f"**Summary:** {result['summary']}\n\n"
                        
                        response += "**Next Steps:** Check official scheme websites, contact local agricultural offices, or visit nearest Common Service Centers for detailed application procedures."
                        
                        return response
                    else:
                        # Standard agricultural response
                        response = f"Based on agricultural knowledge base:\n\n"
                        for i, chunk in enumerate(result['chunks'][:3], 1):  # Limit to top 3 chunks
                            response += f"{i}. {chunk.get('content', '')[:200]}...\n\n"
                        
                        if result.get('summary'):
                            response += f"Summary: {result['summary']}\n\n"
                        
                        if result.get('suggested_actions'):
                            response += f"Recommended actions: {', '.join(result['suggested_actions'])}"
                        
                        return response
                else:
                    return "I couldn't find specific information about that topic in our agricultural knowledge base. Please try rephrasing your question or ask about a different agricultural topic."
                    
            except Exception as e:
                logger.error(f"RAG tool error: {e}")
                return f"I encountered an error accessing agricultural information: {str(e)}"
        

        
        @tool
        async def get_market_info(crop: str = None) -> str:
            """Get market price information for crops."""
            # TODO: Integrate with actual market service
            return "Market prices are stable. Consider selling in next 2-3 weeks."

        # Create a weather tool that can access the agent instance
        @tool
        async def get_weather_info(forecast_days: int = 7, include_agricultural_advice: bool = True) -> str:
            """
            Get comprehensive weather information for agricultural planning using your profile location.
            
            Args:
                forecast_days: Number of days for forecast (1-7, default: 7)
                include_agricultural_advice: Include agricultural recommendations based on weather (default: True)
                
            Returns:
                Weather information and agricultural recommendations for your location
            """
            try:
                # Get user's location from agent context
                if not hasattr(self, 'context') or not self.context or not self.context.location:
                    return "I couldn't find your location in your profile. Please update your profile with your location coordinates to get weather information."
                
                lat = self.context.location.get('lat')
                lon = self.context.location.get('lon')
                
                if not lat or not lon:
                    return "Your profile location coordinates are incomplete. Please update your profile with your complete location (latitude and longitude) to get weather information."
                
                # Create location string for weather tool
                location = f"{lat},{lon}"
                logger.info(f"Using user profile location for weather: {location}")
                
                # Use the weather tool with the user's location
                weather_tool = WeatherTool()
                result = await weather_tool._arun(
                    location=location,
                    forecast_days=forecast_days,
                    include_agricultural_advice=include_agricultural_advice
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Error in weather tool: {e}")
                return f"I encountered an error retrieving weather information: {str(e)}"

        # Initialize Tavily tool
        tavily_tools = get_tavily_tools()
        
        # Get all tools including Tavily tools
        all_tools = [
            get_crop_information,
            get_market_info,
            get_weather_info,  # Use the closure-based weather tool
            GovernmentSchemesTool(),
        ]
        
        # Add Tavily tools if available
        if tavily_tools:
            all_tools.extend(tavily_tools)
            logger.info("Tavily web search tools added to chat agent")
        else:
            logger.warning("Tavily tools not available - web search will be disabled")
        
        return all_tools
    
    def _create_agent(self):
        """Create the LangChain agent."""
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an agricultural advisor for Indian farmers. You have access to a comprehensive knowledge base and tools to help farmers with their agricultural needs.

Your capabilities include:
- Accessing detailed agricultural information from our knowledge base
- Providing comprehensive government scheme information (PM KISAN, PMKSY, PMFBY, etc.)
- Retrieving budget allocations, eligibility criteria, and application processes
- **Providing real-time weather data and agricultural recommendations (automatically uses your profile location - no need to specify location)**
- Accessing market price information for crops
- Giving crop-specific tips and advice
- Supporting multiple languages (English, Hindi, Kannada)
- Analyzing images for agricultural problems
- **NEW: Web search capabilities for real-time information** - You can search the web for the latest news, market updates, government announcements, and current agricultural information

**Weather Tool Usage:**
- **get_weather_info**: Automatically uses the user's profile location - just specify forecast days (1-7) and whether to include agricultural advice
- No need to ask for location - it's automatically retrieved from the user's profile
- Perfect for questions like "What's the weather like?" or "Give me a 5-day forecast"

**Web Search Tools Available:**
- **search_web**: General web search for any topic - use when you need current information
- **search_agricultural_news**: Latest agricultural news and farming updates
- **search_market_prices**: Current market prices and trends for crops

**When to Use Web Search:**
- Questions about current events, recent government announcements, or latest news
- Real-time market information, price updates, or demand trends
- Recent policy changes, new schemes, or updated guidelines
- Current weather patterns, climate updates, or seasonal changes
- Any information that might be time-sensitive or require current data

Always be helpful, accurate, and farmer-friendly. Use the available tools when relevant to provide the most up-to-date and comprehensive information. When in doubt about current information, use the web search tools to get the latest data.

Available tools: {tools}"""),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create the agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True
            )
            
            return agent_executor
            
        except Exception as e:
            logger.error(f"Failed to create LangChain agent: {e}")
            raise
    
    async def process_message(
        self, 
        request: ChatRequest, 
        context: ConversationContext
    ) -> ChatResponse:
        """
        Process incoming message and generate response.
        
        Args:
            request: Chat request with media content
            context: Conversation context
            
        Returns:
            Chat response with text and optional audio
        """
        try:
            self.context = context
            # Handle different media types appropriately
            if request.media_type == MediaType.IMAGE:
                response = await self._process_image_request(request, context)
            else:
                response = await self._process_text_request(request, context)
            
            # Generate audio if requested
            audio_data = await self._generate_audio(response.text, context.language)
            
            return ChatResponse(
                text=response.text,
                audio=audio_data,
                metadata=response.metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                text="I encountered an error processing your request. Please try again.",
                audio=None
            )
    
    async def _process_image_request(
        self, 
        request: ChatRequest, 
        context: ConversationContext
    ) -> ChatResponse:
        """Process image request using Gemini vision capabilities."""
        try:
            # Check if vision is supported
            if not self.supports_vision:
                return ChatResponse(
                    text="I'm sorry, but image analysis is not currently supported. Please send a text description instead.",
                    audio=None,
                    metadata={"error": "vision_not_supported"}
                )
            
            # Validate base64 content
            if not request.content:
                raise ValueError("No image content provided")
            
            # Check content length
            if len(request.content) > 2_000_000:  # ~1.5MB binary limit
                raise ValueError("Image too large. Please use an image under 1MB.")
            
            # Validate base64 format
            try:
                image_data = base64.b64decode(request.content, validate=True)
                logger.debug(f"Base64 validation successful, decoded size: {len(image_data)} bytes")
            except Exception as e:
                logger.error(f"Base64 decode failed: {e}")
                raise ValueError(f"Invalid base64 image data: {e}")
            
            # Check decoded image size
            if len(image_data) > 1_500_000:  # 1.5MB limit
                raise ValueError("Decoded image too large. Please use an image under 1MB.")
            
            # Validate mime type
            mime_type = request.mime_type or "image/jpeg"
            if not mime_type.startswith("image/"):
                mime_type = "image/jpeg"
            
            # Check if mime type is supported
            supported_formats = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]
            if mime_type not in supported_formats:
                logger.warning(f"Unsupported image format: {mime_type}, converting to JPEG")
                mime_type = "image/jpeg"
            
            logger.info(f"Processing image: {mime_type}, size: {len(image_data)} bytes")
            
            # Create image message for LangChain
            image_message = HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{request.content}"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Please analyze this image and provide agricultural advice. User context: Language: {context.language}, Crops: {context.crop_preferences or 'Not specified'}, Location: {context.location or 'Not specified'}"
                    }
                ]
            )
            
            # Process with LangChain agent
            try:
                response = await self.agent.ainvoke({
                    "input": image_message,
                    "chat_history": self._get_chat_history(context),
                    "tools": [tool.name for tool in self.tools]
                })
                
                response_text = response.get("output", "I'm sorry, I couldn't analyze the image.")
                
            except Exception as agent_error:
                logger.error(f"LangChain agent error during image processing: {agent_error}")
                response_text = "I can see you've shared an image, but I'm having trouble analyzing it right now. Please try again in a moment, or describe what you see in the image and I'll help you with agricultural advice."
            
            logger.info(f"Image processed successfully, response length: {len(response_text)}")
            
            return ChatResponse(
                text=response_text,
                audio=None,
                metadata={"media_processed": "image", "image_size": len(image_data)}
            )
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return ChatResponse(
                text=f"I encountered an error analyzing the image: {str(e)}. Please try again with a different image.",
                audio=None
            )
    
    async def _process_text_request(
        self, 
        request: ChatRequest, 
        context: ConversationContext
    ) -> ChatResponse:
        """Process text/audio request using LangChain agent."""
        try:
            # Build input for agent
            agent_input = {
                "input": request.content,
                "chat_history": self._get_chat_history(context),
                "tools": [tool.name for tool in self.tools]
            }
            
            # Process with LangChain agent
            response = await self.agent.ainvoke(agent_input)
            
            response_text = response.get("output", "I'm sorry, I couldn't generate a response.")
            
            # Update chat history
            self._update_chat_history(context, request.content, response_text)
            
            return ChatResponse(
                text=response_text,
                audio=None,
                metadata={"media_processed": "text"}
            )
            
        except Exception as e:
            logger.error(f"Error processing text request: {e}")
            return ChatResponse(
                text="I encountered an error processing your request. Please try again.",
                audio=None
            )
    
    def _get_chat_history(self, context: ConversationContext) -> List:
        """Get chat history for the conversation."""
        session_id = f"{context.client_id}_{context.conversation_id}"
        
        if session_id not in self.chat_sessions:
            return []
        
        return self.chat_sessions[session_id]
    
    def _update_chat_history(self, context: ConversationContext, user_input: str, ai_response: str):
        """Update chat history for the conversation."""
        session_id = f"{context.client_id}_{context.conversation_id}"
        
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = []
        
        # Add user message
        self.chat_sessions[session_id].append(
            HumanMessage(content=user_input)
        )
        
        # Add AI response
        self.chat_sessions[session_id].append(
            AIMessage(content=ai_response)
        )
        
        # Keep only last 10 messages to prevent memory issues
        if len(self.chat_sessions[session_id]) > 10:
            self.chat_sessions[session_id] = self.chat_sessions[session_id][-10:]
    
    async def _generate_audio(self, text: str, language: str) -> Optional[str]:
        """
        Generate audio from text response.
        Note: This is a placeholder - actual audio generation would require
        text-to-speech service integration.
        """
        # TODO: Implement actual TTS service
        logger.info(f"Audio generation requested for text in {language}")
        return None
    
    def cleanup_session(self, session_id: str):
        """Clean up chat session."""
        if session_id in self.chat_sessions:
            try:
                del self.chat_sessions[session_id]
                logger.info(f"Cleaned up session {session_id}")
            except Exception as e:
                logger.warning(f"Error cleaning up session {session_id}: {e}")


# Global agent instance
chat_agent = ChatAgent()
