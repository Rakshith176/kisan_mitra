#!/usr/bin/env python3
"""
Mock Live API Agent for testing purposes.
Simulates Live API responses without requiring actual Google API.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List

logger = logging.getLogger(__name__)

class MockLiveAPIAgent:
    """Mock agent for testing Live API interactions."""
    
    def __init__(self, model: str = None):
        self.model = model or "gemini-live-2.5-flash-preview"
        self.sessions: Dict[str, Any] = {}
        
        logger.info(f"Mock Live API agent initialized with model: {self.model}")
    
    async def create_session(self, session_id: str) -> Any:
        """Create a mock session."""
        try:
            # Store session with metadata
            self.sessions[session_id] = {
                "session": f"mock_session_{session_id}",
                "id": session_id,
                "model": self.model,
                "created_at": datetime.now().isoformat(),
                "history": []
            }
            
            logger.info(f"Created mock Live API session: {session_id}")
            return self.sessions[session_id]["session"]
            
        except Exception as e:
            logger.error(f"Failed to create mock session {session_id}: {e}")
            raise
    
    async def process_realtime_input(
        self, 
        session_id: str, 
        content: str, 
        media_type: str = "text",
        language: str = "en",
        audio_format: str | None = None,
        sample_rate: int | None = None,
    ) -> AsyncGenerator[Dict, None]:
        """
        Process real-time input and stream mock responses.
        """
        try:
            # Create or get session
            if session_id not in self.sessions:
                await self.create_session(session_id)
            
            # Store in history
            self.sessions[session_id]["history"].append({
                "role": "user",
                "content": content,
                "media_type": media_type,
                "timestamp": datetime.now().isoformat()
            })
            
            if media_type == "text":
                # Generate mock response based on input
                mock_response = self._generate_mock_response(content)
                
                # Stream the response in chunks to simulate real-time
                words = mock_response.split()
                chunk_size = 3  # Send 3 words at a time
                
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i + chunk_size])
                    
                    yield {
                        "type": "response",
                        "text": chunk + (" " if i + chunk_size < len(words) else ""),
                        "audio": None,
                        "turn_complete": False,
                        "metadata": {
                            "session_id": session_id,
                            "response_type": "mock_live_api",
                            "chunk_index": i // chunk_size
                        }
                    }
                    
                    # Simulate streaming delay
                    await asyncio.sleep(0.1)
                
                # Final turn complete
                yield {
                    "type": "response",
                    "text": None,
                    "audio": None,
                    "turn_complete": True,
                    "metadata": {
                        "session_id": session_id,
                        "response_type": "mock_live_api"
                    }
                }
                    
            elif media_type == "audio":
                # Handle audio input
                yield {
                    "type": "response",
                    "text": f"I received your audio message ({len(content)} bytes). In the experimental version, I'll respond with text. How can I help you with agricultural advice?",
                    "audio": None,
                    "turn_complete": True,
                    "metadata": {
                        "session_id": session_id,
                        "response_type": "mock_live_api"
                    }
                }
                    
        except Exception as e:
            logger.error(f"Error in mock Live API processing: {e}")
            yield {
                "type": "error",
                "text": f"Sorry, I encountered an error: {str(e)}",
                "audio": None,
                "turn_complete": True
            }
    
    def _generate_mock_response(self, user_input: str) -> str:
        """Generate a mock response based on user input."""
        input_lower = user_input.lower()
        
        if "rice" in input_lower and "cultivation" in input_lower:
            return "Rice cultivation is a crucial agricultural practice. For optimal results, ensure proper water management, use high-quality seeds, and maintain soil fertility. The best time to plant rice is during the monsoon season when there's adequate rainfall. Consider using organic fertilizers and practice crop rotation to maintain soil health."
        
        elif "weather" in input_lower:
            return "Weather plays a vital role in agricultural success. Monitor local weather forecasts regularly and plan your farming activities accordingly. During monsoon, ensure proper drainage to prevent waterlogging. In dry seasons, implement irrigation systems to maintain crop health."
        
        elif "fertilizer" in input_lower or "fertiliser" in input_lower:
            return "Fertilizers are essential for crop growth. Use organic fertilizers like compost and manure for sustainable farming. Chemical fertilizers should be applied in recommended quantities to avoid soil degradation. Always test your soil before applying fertilizers to understand nutrient requirements."
        
        elif "pest" in input_lower or "disease" in input_lower:
            return "Pest and disease management is crucial for healthy crops. Use integrated pest management techniques combining biological, cultural, and chemical methods. Regular monitoring helps in early detection. Consider using neem-based solutions as natural pest repellents."
        
        elif "government" in input_lower or "scheme" in input_lower:
            return "The government offers various agricultural schemes to support farmers. PM-KISAN provides direct income support, while PMKSY focuses on irrigation infrastructure. Check with your local agricultural office for eligibility and application procedures for these schemes."
        
        elif "market" in input_lower or "price" in input_lower:
            return "Market prices for agricultural products vary based on demand, season, and quality. Stay updated with local mandi prices through government portals. Consider value addition and direct marketing to improve profitability. Building relationships with local traders can help get better prices."
        
        elif "hello" in input_lower or "hi" in input_lower:
            return "Hello! I'm your agricultural assistant. I can help you with farming advice, weather information, government schemes, market prices, and pest management. What specific agricultural topic would you like to know more about?"
        
        else:
            return "Thank you for your question about agriculture. I can help you with various topics including crop cultivation, weather management, government schemes, market prices, pest control, and sustainable farming practices. Please let me know what specific information you need."
    
    async def execute_tool(self, tool_name: str, parameters: Dict) -> str:
        """Execute a mock tool and return the result."""
        try:
            logger.info(f"Executing mock tool: {tool_name} with parameters: {parameters}")
            
            if tool_name == "get_weather_info":
                return "Weather information: Currently sunny with scattered clouds. Temperature around 28°C. Good conditions for outdoor farming activities."
            elif tool_name == "get_crop_information":
                return "Crop information: Based on your query, here are some general agricultural best practices for healthy crop growth and optimal yields."
            elif tool_name == "get_government_schemes":
                return "Government schemes: PM-KISAN, PMKSY, and other agricultural support programs are available. Contact your local agricultural office for details."
            else:
                return f"Mock tool '{tool_name}' executed successfully with parameters: {parameters}"
                
        except Exception as e:
            logger.error(f"Error executing mock tool {tool_name}: {e}")
            return f"Error executing mock tool: {str(e)}"
    
    async def close_session(self, session_id: str) -> None:
        """Close a mock session."""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Closed mock Live API session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error closing mock session {session_id}: {e}")
    
    async def cleanup_all_sessions(self) -> None:
        """Close all mock sessions."""
        try:
            session_ids = list(self.sessions.keys())
            for session_id in session_ids:
                await self.close_session(session_id)
                
            logger.info("Closed all mock Live API sessions")
            
        except Exception as e:
            logger.error(f"Error closing all mock sessions: {e}")
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a mock session."""
        if session_id in self.sessions:
            session_data = self.sessions[session_id].copy()
            return session_data
        return {}
    
    def get_all_sessions_info(self) -> Dict[str, Dict]:
        """Get information about all mock sessions."""
        return {session_id: self.get_session_info(session_id) for session_id in self.sessions}


# Create mock agent instance
mock_live_api_agent = MockLiveAPIAgent()
