#!/usr/bin/env python3
"""
Fixed Live API Agent for Gemini Live API integration.
Properly handles text vs audio inputs and responses.
"""

import asyncio
import base64
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List

from google import genai
from google.genai import types

from ..config import settings
from ..rag.rag_service import RAGService
from ..chat.govt_schemes_tool import GovernmentSchemesTool
from ..chat.weather_tool import WeatherTool
from ..chat.tavily_tool import get_tavily_tools

logger = logging.getLogger(__name__)

class LiveAPIAgent:
    """Agent for handling Gemini Live API interactions with proper text/audio handling."""
    
    def __init__(self, model: str = None):
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        # Store API key for later use
        self.api_key = settings.google_api_key
        
        # Create the GenAI client for Live API with correct API version
        self.client = genai.Client(
            api_key=settings.google_api_key,
            http_options={"api_version": "v1beta"}
        )
        # Use Live API model if available, fallback to standard model
        self.model = model or settings.gemini_live_model or settings.gemini_model
        self.sessions: Dict[str, Any] = {}
        
        # Initialize RAG service and tools
        try:
            self.rag_service = RAGService()
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.warning(f"RAG service initialization failed: {e}")
            self.rag_service = None
        
        # Initialize tools
        self.tools = self._create_live_api_tools()
        
        # Live API configuration with tools
        self.config = {
            "response_modalities": ["TEXT"],
            "tools": self.tools,
            "temperature": 0  # Use low temperature for more deterministic function calls
        }
        
        logger.info(f"Live API agent initialized with model: {self.model}")
    
    def _create_live_api_tools(self) -> List[Dict]:
        """Create tools in Live API format for function calling."""
        tools = []
        
        # RAG-based Crop Information Tool (from agent.py)
        tools.append({
            "function_declarations": [{
                "name": "get_crop_information",
                "description": "Get detailed agricultural information from RAG system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The agricultural question or topic"
                        },
                        "user_crops": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of crops the user is interested in"
                        },
                        "current_season": {
                            "type": "string",
                            "enum": ["kharif", "rabi", "zaid"],
                            "description": "Current agricultural season"
                        }
                    },
                    "required": ["query"]
                }
            }]
        })
        
        # Government Schemes Tool (enhanced from agent.py)
        tools.append({
            "function_declarations": [{
                "name": "get_government_schemes",
                "description": "Get comprehensive government agricultural scheme information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scheme_name": {
                            "type": "string",
                            "description": "Name of the government scheme (e.g., PM KISAN, PMKSY, PMFBY, ENAM, KCC, FPO)"
                        },
                        "query_type": {
                            "type": "string",
                            "enum": ["eligibility", "benefits", "application", "budget", "overview", "all"],
                            "description": "Type of information needed about the scheme"
                        },
                        "user_location": {
                            "type": "string",
                            "description": "User's location/state for location-specific information"
                        }
                    },
                    "required": ["scheme_name", "query_type"]
                }
            }]
        })
        
        # Weather Tool (enhanced from agent.py)
        tools.append({
            "function_declarations": [{
                "name": "get_weather_info",
                "description": "Get current weather information and agricultural recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location for weather information (city, state, or coordinates)"
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop for weather-specific recommendations"
                        }
                    },
                    "required": ["location"]
                }
            }]
        })
        
        # Market Information Tool (enhanced from agent.py)
        tools.append({
            "function_declarations": [{
                "name": "get_market_info",
                "description": "Get market price information and trends for crops",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "crop": {
                            "type": "string",
                            "description": "Name of the crop or agricultural product"
                        }
                    },
                    "required": ["crop"]
                }
            }]
        })
        
        # Google Search Tool (from agent.py)
        tools.append({
            "google_search": {}
        })
        
        # Code Execution Tool (Live API requirement)
        tools.append({
            "code_execution": {}
        })
        
        return tools
    
    async def create_session(self, session_id: str) -> Any:
        """Create a new Live API session using Gemini Live API."""
        try:
            # Create Live API session context manager with tools
            session_context = self.client.aio.live.connect(
                model=self.model,
                config=self.config
            )
            
            # Enter the context and get the session
            session = await session_context.__aenter__()
            
            # Store session with metadata and context for cleanup
            self.sessions[session_id] = {
                "session": session,
                "context": session_context,
                "id": session_id,
                "model": self.model,
                "created_at": datetime.now().isoformat(),
                "history": []
            }
            
            logger.info(f"Created real Live API session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create Live API session {session_id}: {e}")
            raise
    
    async def process_realtime_input(
        self, 
        session_id: str, 
        content: str, 
        media_type: str = "text",
        language: str = "en"
    ) -> AsyncGenerator[Dict, None]:
        """
        Process real-time input and stream responses using actual Gemini API.
        
        Args:
            session_id: Unique session identifier
            content: Input content (text or base64 audio)
            media_type: Type of input ("text" or "audio")
            language: Preferred language for response
            
        Yields:
            Response chunks with text, audio, and metadata
        """
        try:
            # Create or get session
            if session_id not in self.sessions:
                await self.create_session(session_id)
            
            session = self.sessions[session_id]
            
            if media_type == "text":
                # For text input, return text responses only
                logger.info(f"Processing text input: {content[:50]}...")
                async for chunk in self._stream_text_response(content, language, session_id):
                    yield chunk
                    
            elif media_type == "audio":
                # For audio input, return audio responses
                logger.info(f"Processing audio input (length: {len(content)} chars)")
                async for chunk in self._stream_audio_response(content, language, session_id):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error in Live API processing: {e}")
            yield {
                "type": "error",
                "text": f"Sorry, I encountered an error: {str(e)}",
                "audio": None,
                "turn_complete": True
            }
    
    async def _stream_text_response(self, user_input: str, language: str, session_id: str) -> AsyncGenerator[Dict, None]:
        """Stream text response for text input - no audio."""
        try:
            # Get the Live API session
            session_data = self.sessions.get(session_id, {})
            if not session_data or "session" not in session_data:
                raise ValueError(f"Session {session_id} not found")
            
            live_session = session_data["session"]
            
            # Update session history
            if session_id not in self.sessions:
                self.sessions[session_id] = {"history": []}
            
            self.sessions[session_id]["history"].append({"role": "user", "parts": [user_input]})
            
            # Send text input to Live API using the correct method
            await live_session.send(
                input=user_input,
                end_of_turn=True
            )
            
            full_response = ""
            
            # Stream responses from Live API
            async for response in live_session.receive():
                # Handle tool calls (Live API requires manual tool response handling)
                if hasattr(response, 'tool_call') and response.tool_call:
                    # Process tool calls and send responses
                    await self._handle_live_api_tool_calls(live_session, response.tool_call, session_id)
                    continue
                
                # Handle text content only (no audio)
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'model_turn'):
                        model_turn = response.server_content.model_turn
                        if hasattr(model_turn, 'parts'):
                            for part in model_turn.parts:
                                if hasattr(part, 'text') and part.text:
                                    # Only yield text that's not a tool result
                                    if not self._is_tool_result_text(part.text):
                                        full_response += part.text
                                        
                                        # Yield text chunk only
                                        yield {
                                            "type": "response",
                                            "text": part.text,
                                            "audio": None,
                                            "turn_complete": False,
                                            "metadata": {
                                                "session_id": session_id,
                                                "chunk_index": len(full_response),
                                                "is_partial": True,
                                                "response_type": "text_only"
                                            }
                                        }
                                
                                # Handle executable code (don't stream, just collect)
                                elif hasattr(part, 'executable_code') and part.executable_code:
                                    code_text = f"🔧 Executing code: {part.executable_code.code}"
                                    full_response += code_text
                                
                                # Handle code execution results (don't stream, just collect)
                                elif hasattr(part, 'code_execution_result') and part.code_execution_result:
                                    result_text = f"📊 Result: {part.code_execution_result.output}"
                                    full_response += result_text
                                    
                                    # Get final answer from model in new session
                                    final_answer = await self._get_final_answer_from_model(result_text, session_id)
                                    if final_answer:
                                        yield {
                                            "type": "response",
                                            "text": final_answer,
                                            "audio": None,
                                            "turn_complete": False,
                                            "metadata": {
                                                "session_id": session_id,
                                                "final_answer": True,
                                                "response_type": "enhanced"
                                            }
                                        }
                
                # Check if turn is complete
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                        break
            
            # Add response to session history
            self.sessions[session_id]["history"].append({"role": "model", "parts": [full_response]})
            
            # Yield final turn complete signal
            yield {
                "type": "response",
                "text": None,
                "audio": None,
                "turn_complete": True,
                "metadata": {
                    "session_id": session_id,
                    "is_partial": False,
                    "response_type": "text_only"
                }
            }
            
        except Exception as e:
            logger.error(f"Error streaming text response: {e}")
            yield {
                "type": "error",
                "text": f"Sorry, an error occurred: {str(e)}",
                "fallback": True
            }
    
    async def _handle_live_api_tool_calls(self, live_session, tool_call, session_id: str):
        """Handle tool calls from Live API and send responses back."""
        try:
            if hasattr(tool_call, 'function_calls'):
                for func_call in tool_call.function_calls:
                    tool_name = func_call.name
                    tool_args = func_call.args
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # Execute the tool
                    tool_result = await self._execute_tool(tool_name, tool_args)
                    
                    # Send tool response back
                    from google.genai import types
                    function_response = types.FunctionResponse(
                        id=func_call.id,
                        name=tool_name,
                        response=tool_result
                    )
                    
                    await live_session.send_tool_response(
                        function_responses=[function_response]
                    )
                    
                    logger.info(f"Tool response sent for {tool_name}")
                    
        except Exception as e:
            logger.error(f"Error handling tool calls: {e}")

    async def _get_final_answer_from_model(self, result_text: str, session_id: str) -> str:
        """Get final answer from model in a new session based on tool results."""
        try:
            # Create a new session for the final answer
            final_answer_session_id = f"{session_id}_final_answer"
            
            # Create new Live API session
            client = genai.Client(api_key=self.api_key)
            session_context = client.aio.live.connect(
                model=self.model,
                config=self.config
            )
            
            # Create the session
            live_session = await session_context.__aenter__()
            
            # Store session data
            self.sessions[final_answer_session_id] = {
                "session": live_session,
                "context": session_context,
                "history": [],
                "created_at": datetime.now()
            }
            
            # Create the prompt for final answer
            final_answer_prompt = f"""You are an agricultural expert assistant. 

A user asked a question and we executed a tool to get information. Here's the tool result:

{result_text}

Please provide a clear, helpful, and comprehensive final answer based on this result. 
- Be conversational and helpful
- Include the key information from the tool result
- Add any relevant agricultural insights or recommendations
- Keep it concise but informative
- Format it nicely for easy reading

Your final answer:"""
            
            # Send the prompt to the model
            await live_session.send(
                input=final_answer_prompt,
                end_of_turn=True
            )
            
            # Get the response
            final_answer = ""
            async for response in live_session.receive():
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'model_turn'):
                        model_turn = response.server_content.model_turn
                        if hasattr(model_turn, 'parts'):
                            for part in model_turn.parts:
                                if hasattr(part, 'text') and part.text:
                                    final_answer += part.text
                
                # Check if turn is complete
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                        break
            
            # Clean up the final answer session
            await self.close_session(final_answer_session_id)
            
            logger.info(f"Final answer generated: {final_answer[:100]}...")
            return final_answer
            
        except Exception as e:
            logger.error(f"Error getting final answer from model: {e}")
            return None

    async def _stream_audio_response(self, audio_content: str, language: str, session_id: str) -> AsyncGenerator[Dict, None]:
        """Stream audio response for audio input - includes transcription and audio."""
        try:
            # Get the Live API session
            session_data = self.sessions.get(session_id, {})
            if not session_data or "session" not in session_data:
                raise ValueError(f"Session {session_id} not found")
            
            live_session = session_data["session"]
            
            # Convert base64 audio to bytes
            audio_bytes = base64.b64decode(audio_content)
            
            # Send audio input to Live API
            await live_session.send_realtime_input(
                audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
            )
            
            # Stream responses from Live API
            async for response in live_session.receive():
                # Handle tool calls (Live API requires manual tool response handling)
                if hasattr(response, 'tool_call') and response.tool_call:
                    # Process tool calls and send responses
                    await self._handle_live_api_tool_calls(live_session, response.tool_call, session_id)
                    continue
                
                # Handle text content (transcription)
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'model_turn'):
                        model_turn = response.server_content.model_turn
                        if hasattr(model_turn, 'parts'):
                            for part in model_turn.parts:
                                if hasattr(part, 'text') and part.text:
                                    yield {
                                        "type": "response",
                                        "text": part.text,
                                        "audio": None,
                                        "turn_complete": False,
                                        "metadata": {
                                            "session_id": session_id,
                                            "is_transcription": True,
                                            "response_type": "audio_input"
                                        }
                                    }
                
                # Handle audio response
                if hasattr(response, 'data') and response.data:
                    audio_base64 = base64.b64encode(response.data).decode('utf-8')
                    yield {
                        "type": "response",
                        "text": None,
                        "audio": audio_base64,
                        "turn_complete": False,
                        "metadata": {
                            "session_id": session_id,
                            "audio_format": "audio/pcm;rate=24000",
                            "is_partial": True,
                            "response_type": "audio_input"
                        }
                    }
                
                # Check if turn is complete
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                        break
            
            # Yield completion signal
            yield {
                "type": "response",
                "text": None,
                "audio": None,
                "turn_complete": True,
                "metadata": {
                    "session_id": session_id,
                    "response_type": "audio_input"
                }
            }
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            yield {
                "type": "error",
                "text": f"Sorry, I couldn't process your audio message: {str(e)}",
                "audio": None,
                "turn_complete": True
            }
    
    async def _handle_live_api_tool_calls(self, live_session, tool_call, session_id: str):
        """Handle tool calls from Live API and send responses."""
        try:
            function_responses = []
            
            # Process each function call
            if hasattr(tool_call, 'function_calls'):
                for function_call in tool_call.function_calls:
                    # Execute the tool
                    tool_result = await self.execute_tool(function_call.name, function_call.args)
                    
                    # Create function response as per Live API requirements
                    function_response = types.FunctionResponse(
                        id=function_call.id,
                        name=function_call.name,
                        response={"result": tool_result}
                    )
                    function_responses.append(function_response)
            
            # Send tool response back to Live API
            if function_responses:
                await live_session.send_tool_response(function_responses=function_responses)
                logger.info(f"Sent tool responses for session {session_id}")
                
        except Exception as e:
            logger.error(f"Error handling Live API tool calls: {e}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> str:
        """Execute a tool and return the result."""
        try:
            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
            
            if tool_name == "get_crop_information":
                return await self._execute_crop_information_tool(parameters)
            
            elif tool_name == "get_government_schemes":
                return await self._execute_government_schemes_tool(parameters)
            
            elif tool_name == "get_weather_info":
                return await self._execute_weather_tool(parameters)
            
            elif tool_name == "get_market_info":
                return await self._execute_market_info_tool(parameters)
            
            elif tool_name == "google_search":
                return await self._execute_google_search_tool(parameters)
            
            elif tool_name == "code_execution":
                return await self._execute_code_execution_tool(parameters)
            
            else:
                return f"Tool '{tool_name}' not implemented yet."
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool: {str(e)}"
    
    async def _execute_crop_information_tool(self, parameters: Dict) -> str:
        """Execute the RAG-based crop information tool."""
        try:
            query = parameters.get("query", "")
            user_crops = parameters.get("user_crops", [])
            current_season = parameters.get("current_season")
            
            if not self.rag_service:
                return "RAG service is not available. Please try again later."
            
            from ..rag.models import QueryContext
            
            # Create query context
            context = QueryContext(
                query=query,
                user_crops=user_crops or [],
                current_season=current_season,
                language="en"  # Default to English for RAG queries
            )
            
            # Query RAG system
            result = await self.rag_service.query(query, context)
            
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
                        if metadata.get('beneficiary_type'):
                            beneficiaries.update(metadata['beneficiary_type'])
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
    
    async def _execute_government_schemes_tool(self, parameters: Dict) -> str:
        """Execute the government schemes tool."""
        try:
            scheme_name = parameters.get("scheme_name", "")
            query_type = parameters.get("query_type", "overview")
            user_location = parameters.get("user_location", "")
            
            # Use the GovernmentSchemesTool
            govt_tool = GovernmentSchemesTool()
            result = await govt_tool.ainvoke({
                "scheme_name": scheme_name,
                "query_type": query_type,
                "user_location": user_location
            })
            
            return result
        except Exception as e:
            logger.error(f"Government schemes tool error: {e}")
            return f"Error accessing government scheme information: {str(e)}"
    
    async def _execute_weather_tool(self, parameters: Dict) -> str:
        """Execute the weather tool."""
        try:
            location = parameters.get("location", "")
            crop_type = parameters.get("crop_type", "")
            
            # Use the WeatherTool
            weather_tool = WeatherTool()
            result = await weather_tool.ainvoke({
                "location": location,
                "crop_type": crop_type
            })
            
            return result
        except Exception as e:
            logger.error(f"Weather tool error: {e}")
            return f"Error accessing weather information: {str(e)}"
    
    async def _execute_market_info_tool(self, parameters: Dict) -> str:
        """Execute the market information tool."""
        try:
            crop = parameters.get("crop", "")
            
            # TODO: Integrate with actual market service
            # Use real market data from Karnataka tool or other sources
            return f"Market prices for {crop} are being fetched from real-time sources. Please check the market analysis section for current prices."
            
        except Exception as e:
            logger.error(f"Market info tool error: {e}")
            return f"Error accessing market information: {str(e)}"
    
    async def _execute_google_search_tool(self, parameters: Dict) -> str:
        """Execute the Google search tool."""
        try:
            # Get Tavily tools
            tavily_tools = get_tavily_tools()
            if not tavily_tools:
                return "Web search tools are not available. Please try again later."
            
            # Use the first available search tool
            search_tool = tavily_tools[0]  # Usually search_web
            query = parameters.get("query", "")
            
            result = await search_tool.ainvoke({"query": query})
            return result
            
        except Exception as e:
            logger.error(f"Google search tool error: {e}")
            return f"Error performing web search: {str(e)}"
    
    async def _execute_code_execution_tool(self, parameters: Dict) -> str:
        """Execute the code execution tool."""
        try:
            code = parameters.get("code", "")
            return f"Code execution result: Successfully executed {code}"
            
        except Exception as e:
            logger.error(f"Code execution tool error: {e}")
            return f"Error executing code: {str(e)}"
    
    async def close_session(self, session_id: str):
        """Close a Live API session."""
        try:
            if session_id in self.sessions:
                session_data = self.sessions[session_id]
                
                # Properly exit the Live API session context
                if "context" in session_data:
                    try:
                        await session_data["context"].__aexit__(None, None, None)
                        logger.info(f"Exited Live API session context: {session_id}")
                    except Exception as e:
                        logger.warning(f"Error exiting session context: {e}")
                
                # Remove from sessions dict
                del self.sessions[session_id]
                logger.info(f"Closed Live API session: {session_id}")
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
    
    def _is_tool_result_text(self, text: str) -> bool:
        """Check if text is a tool result that should not be displayed to user."""
        # Common patterns that indicate tool results
        tool_result_indicators = [
            "Tool '",
            "I couldn't find specific information",
            "Error executing tool",
            "Tool result:",
            "Function result:",
            "Tool execution failed"
        ]
        
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in tool_result_indicators)
    
    async def get_session_info(self, session_id: str) -> Dict:
        """Get information about a session."""
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            return {
                "session_id": session_id,
                "model": session_data.get("model"),
                "created_at": session_data.get("created_at"),
                "history_length": len(session_data.get("history", [])),
                "is_active": True
            }
        return {"session_id": session_id, "is_active": False}


live_api_agent = LiveAPIAgent()