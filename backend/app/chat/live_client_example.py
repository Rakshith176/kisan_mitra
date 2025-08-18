"""
Example client for testing Gemini Live API.
This demonstrates how to connect and interact with the Live API endpoints.
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveAPIClient:
    """Example client for testing Live API functionality."""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        self.websocket = None
    
    async def connect(self, session_id: str = None):
        """Connect to Live API WebSocket."""
        if not session_id:
            session_id = f"test_session_{asyncio.get_event_loop().time()}"
        
        self.session_id = session_id
        websocket_url = f"{self.base_url}/live/ws/{session_id}"
        
        try:
            self.websocket = await websockets.connect(websocket_url)
            logger.info(f"Connected to Live API: {websocket_url}")
            
            # Start listening for responses
            asyncio.create_task(self._listen_for_responses())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def _listen_for_responses(self):
        """Listen for responses from the Live API."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_response(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error listening for responses: {e}")
    
    async def _handle_response(self, data: Dict[str, Any]):
        """Handle response from Live API."""
        response_type = data.get("type")
        
        if response_type == "live_response":
            chunk = data.get("chunk", {})
            text = chunk.get("text")
            audio = chunk.get("audio")
            turn_complete = chunk.get("turn_complete", False)
            
            if text:
                logger.info(f"Text response: {text}")
            
            if audio:
                logger.info(f"Audio response received: {len(audio)} base64 chars")
            
            if turn_complete:
                logger.info("Turn complete")
                
        elif response_type == "tool_result":
            tool_name = data.get("tool_name")
            result = data.get("result")
            logger.info(f"Tool {tool_name} result: {result}")
            
        elif response_type == "error":
            error_msg = data.get("message")
            logger.error(f"Live API error: {error_msg}")
            
        elif response_type == "session_config_updated":
            logger.info("Session configuration updated")
            
        else:
            logger.info(f"Unknown response type: {response_type}")
    
    async def send_text_message(self, content: str, language: str = "en"):
        """Send a text message to the Live API."""
        if not self.websocket:
            logger.error("Not connected to Live API")
            return
        
        message = {
            "type": "text",
            "content": content,
            "language": language
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent text message: {content[:50]}...")
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
    
    async def send_audio_message(self, audio_content: str, language: str = "en"):
        """Send an audio message to the Live API."""
        if not self.websocket:
            logger.error("Not connected to Live API")
            return
        
        message = {
            "type": "audio",
            "content": audio_content,  # Base64 encoded audio
            "language": language
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent audio message: {len(audio_content)} base64 chars")
        except Exception as e:
            logger.error(f"Error sending audio message: {e}")
    
    async def request_tool_execution(self, tool_name: str, parameters: Dict[str, Any]):
        """Request tool execution."""
        if not self.websocket:
            logger.error("Not connected to Live API")
            return
        
        message = {
            "type": "tool_request",
            "tool_name": tool_name,
            "parameters": parameters
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Requested tool execution: {tool_name}")
        except Exception as e:
            logger.error(f"Error requesting tool execution: {e}")
    
    async def update_session_config(self, context: Dict[str, Any]):
        """Update session configuration."""
        if not self.websocket:
            logger.error("Not connected to Live API")
            return
        
        message = {
            "type": "session_config",
            "context": context
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info("Updated session configuration")
        except Exception as e:
            logger.error(f"Error updating session config: {e}")
    
    async def disconnect(self):
        """Disconnect from Live API."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from Live API")


async def test_live_api():
    """Test the Live API functionality."""
    client = LiveAPIClient()
    
    try:
        # Connect to Live API
        if not await client.connect():
            logger.error("Failed to connect to Live API")
            return
        
        # Wait a moment for connection to establish
        await asyncio.sleep(1)
        
        # Test 1: Send text message
        logger.info("=== Testing Text Message ===")
        await client.send_text_message(
            "Hello! I'm a farmer from Karnataka. Can you tell me about PM KISAN scheme?",
            language="en"
        )
        
        # Wait for response
        await asyncio.sleep(5)
        
        # Test 2: Request tool execution
        logger.info("=== Testing Tool Execution ===")
        await client.request_tool_execution(
            "get_government_schemes",
            {
                "scheme_name": "PM KISAN",
                "query_type": "eligibility",
                "user_location": "Karnataka"
            }
        )
        
        # Wait for response
        await asyncio.sleep(5)
        
        # Test 3: Update session context
        logger.info("=== Testing Session Config Update ===")
        await client.update_session_config({
            "client_id": "test_client",
            "conversation_id": "test_conversation",
            "language": "en",
            "location": "Karnataka",
            "crop_preferences": ["rice", "maize"]
        })
        
        # Wait for response
        await asyncio.sleep(2)
        
        # Test 4: Send another text message
        logger.info("=== Testing Follow-up Message ===")
        await client.send_text_message(
            "What about weather conditions for rice farming in my area?",
            language="en"
        )
        
        # Wait for response
        await asyncio.sleep(5)
        
        # Test 5: Request weather tool
        logger.info("=== Testing Weather Tool ===")
        await client.request_tool_execution(
            "get_weather_info",
            {
                "location": "Karnataka",
                "crop_type": "rice"
            }
        )
        
        # Wait for response
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Test error: {e}")
    
    finally:
        # Disconnect
        await client.disconnect()


async def test_audio_message():
    """Test audio message functionality (placeholder)."""
    client = LiveAPIClient()
    
    try:
        # Connect to Live API
        if not await client.connect():
            logger.error("Failed to connect to Live API")
            return
        
        # Wait for connection
        await asyncio.sleep(1)
        
        # Create dummy audio content (base64 encoded)
        # In real usage, this would be actual audio data
        dummy_audio = base64.b64encode(b"dummy_audio_data").decode()
        
        logger.info("=== Testing Audio Message ===")
        await client.send_audio_message(dummy_audio, language="en")
        
        # Wait for response
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Audio test error: {e}")
    
    finally:
        await client.disconnect()


if __name__ == "__main__":
    """Run Live API tests."""
    logger.info("Starting Live API tests...")
    
    # Run text message test
    asyncio.run(test_live_api())
    
    # Run audio message test
    # asyncio.run(test_audio_message())
    
    logger.info("Live API tests completed.")
