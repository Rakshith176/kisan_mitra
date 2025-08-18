"""
Router for Gemini Live API endpoints.
This provides real-time chat capabilities with simplified tool support.
"""

import asyncio
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json

# Use real Live API agent
from app.chat.live_agent import live_api_agent
# from app.chat.mock_live_agent import mock_live_api_agent as live_api_agent  # Commented out mock agent

from app.chat.schemas import ConversationContext
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/live", tags=["Live API"])


class LiveAPIConnectionManager:
    """Manages Live API WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_contexts: Dict[str, ConversationContext] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"Live API WebSocket connected: {session_id}")
        
        # Send experimental banner message
        try:
            await websocket.send_json({
                "type": "experimental_banner",
                "title": "🧪 EXPERIMENTAL LIVE API",
                "message": "This Live API integration is experimental for multilingual audio responses. It demonstrates real-time voice conversations with AI agricultural assistance.",
                "details": "Features: Real-time streaming, voice input/output, tool integration, multilingual support",
                "status": "demo_mode"
            })
        except Exception as e:
            logger.warning(f"Failed to send experimental banner: {e}")
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
        logger.info(f"Live API WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send a message to a specific client."""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)


# Global connection manager
connection_manager = LiveAPIConnectionManager()


@router.websocket("/ws/{session_id}")
async def live_api_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time Live API conversations.
    
    Supports:
    - Text input/output
    - Audio input (simplified)
    - Session management
    - Real-time streaming responses
    """
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message based on type
            message_type = data.get("type", "text")
            
            if message_type == "text":
                await _handle_text_message(session_id, data)
            elif message_type == "audio":
                await _handle_audio_message(session_id, data)
            elif message_type == "tool_request":
                await _handle_tool_request(session_id, data)
            elif message_type == "session_config":
                await _handle_session_config(session_id, data)
            else:
                await connection_manager.send_message(session_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"Live API WebSocket disconnected: {session_id}")
        connection_manager.disconnect(session_id)
        await live_api_agent.close_session(session_id)
    except Exception as e:
        logger.error(f"Error in Live API WebSocket {session_id}: {e}")
        await connection_manager.send_message(session_id, {
            "type": "error",
            "message": f"Internal error: {str(e)}"
        })
        connection_manager.disconnect(session_id)
        await live_api_agent.close_session(session_id)


async def _handle_text_message(session_id: str, data: Dict[str, Any]):
    """Handle text message from client."""
    try:
        content = data.get("content", "")
        language = data.get("language", "en")
        
        if not content:
            await connection_manager.send_message(session_id, {
                "type": "error",
                "message": "No content provided"
            })
            return
        
        # Process with Live API agent
        async for response_chunk in live_api_agent.process_realtime_input(
            session_id=session_id,
            content=content,
            media_type="text",
            language=language
        ):
            # Send each chunk immediately
            await connection_manager.send_message(session_id, {
                "type": "live_response",
                "chunk": response_chunk,
                "session_id": session_id
            })
            
            # Check if turn is complete
            if response_chunk.get("turn_complete", False):
                break
                
    except Exception as e:
        logger.error(f"Error handling text message for {session_id}: {e}")
        await connection_manager.send_message(session_id, {
            "type": "error",
            "message": f"Error processing text: {str(e)}"
        })


async def _handle_audio_message(session_id: str, data: Dict[str, Any]):
    """Handle audio message from client."""
    try:
        audio_content = data.get("content", "")
        language = data.get("language", "en")
        audio_format = data.get("format")
        sample_rate = data.get("sample_rate")
        
        if not audio_content:
            await connection_manager.send_message(session_id, {
                "type": "error",
                "message": "No audio content provided"
            })
            return
        
        # Process with Live API agent (simplified audio handling)
        async for response_chunk in live_api_agent.process_realtime_input(
            session_id=session_id,
            content=audio_content,
            media_type="audio",
            language=language,
            audio_format=audio_format,
            sample_rate=sample_rate
        ):
            # Send each chunk immediately
            await connection_manager.send_message(session_id, {
                "type": "live_response",
                "chunk": response_chunk,
                "session_id": session_id
            })
            
            # Check if turn is complete
            if response_chunk.get("turn_complete", False):
                break
                
    except Exception as e:
        logger.error(f"Error handling audio message for {session_id}: {e}")
        await connection_manager.send_message(session_id, {
            "type": "error",
            "message": f"Error processing audio: {str(e)}"
        })


async def _handle_tool_request(session_id: str, data: Dict[str, Any]):
    """Handle tool execution request from client."""
    try:
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})
        
        if not tool_name:
            await connection_manager.send_message(session_id, {
                "type": "error",
                "message": "No tool name provided"
            })
            return
        
        # Execute tool
        result = await live_api_agent.execute_tool(tool_name, parameters)
        
        # Send tool result
        await connection_manager.send_message(session_id, {
            "type": "tool_result",
            "tool_name": tool_name,
            "result": result,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name} for {session_id}: {e}")
        await connection_manager.send_message(session_id, {
            "type": "error",
            "message": f"Error executing tool: {str(e)}"
        })


async def _handle_session_config(session_id: str, data: Dict[str, Any]):
    """Handle session configuration updates."""
    try:
        # Update session context
        context_data = data.get("context", {})
        if context_data:
            context = ConversationContext(**context_data)
            connection_manager.session_contexts[session_id] = context
            
            await connection_manager.send_message(session_id, {
                "type": "session_config_updated",
                "session_id": session_id
            })
            
    except Exception as e:
        logger.error(f"Error updating session config for {session_id}: {e}")
        await connection_manager.send_message(session_id, {
            "type": "error",
            "message": f"Error updating session config: {str(e)}"
        })


@router.post("/session/{session_id}/close")
async def close_live_session(session_id: str):
    """Close a Live API session."""
    try:
        await live_api_agent.close_session(session_id)
        connection_manager.disconnect(session_id)
        
        return {"message": f"Session {session_id} closed successfully"}
        
    except Exception as e:
        logger.error(f"Error closing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error closing session: {str(e)}")


@router.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get status of a Live API session."""
    try:
        is_active = session_id in live_api_agent.sessions
        has_connection = session_id in connection_manager.active_connections
        
        return {
            "session_id": session_id,
            "is_active": is_active,
            "has_connection": has_connection,
            "status": "active" if is_active and has_connection else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Error getting session status for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session status: {str(e)}")


@router.post("/cleanup")
async def cleanup_all_sessions():
    """Clean up all active Live API sessions."""
    try:
        await live_api_agent.cleanup_all_sessions()
        
        # Close all WebSocket connections
        for session_id in list(connection_manager.active_connections.keys()):
            connection_manager.disconnect(session_id)
        
        return {"message": "All sessions cleaned up successfully"}
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")


@router.get("/tools")
async def get_available_tools():
    """Get list of available tools for Live API."""
    try:
        tools = ["get_weather_info", "get_crop_information", "get_government_schemes"]
        return {
            "tools": tools,
            "count": len(tools),
            "note": "Tools are simplified in experimental version"
        }
        
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")


@router.post("/test")
async def test_live_api():
    """Test endpoint to verify Live API is working."""
    try:
        # Test basic functionality
        test_session_id = "test_session"
        
        # Create a test session
        session = await live_api_agent.create_session(test_session_id)
        
        # Close test session
        await live_api_agent.close_session(test_session_id)
        
        return {
            "status": "success",
            "message": "Live API is working correctly",
            "model": live_api_agent.model,
            "note": "Simplified experimental version"
        }
        
    except Exception as e:
        logger.error(f"Live API test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Live API test failed: {str(e)}")
