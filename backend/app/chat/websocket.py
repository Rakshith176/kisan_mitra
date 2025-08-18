"""
WebSocket implementation for real-time chat with multimodal support.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState

from .agent import chat_agent
from .schemas import (
    WebSocketMessage, ChatRequest, ChatResponse, 
    ConversationContext, MediaType, ChatMessage
)

logger = logging.getLogger(__name__)


class ChatWebSocket:
    """
    WebSocket handler for real-time chat conversations.
    Supports text, image, and audio inputs with text and audio outputs.
    """
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
    async def connect(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        client_id: str,
        language: str = "en"
    ):
        """Accept WebSocket connection and set up conversation context."""
        try:
            await websocket.accept()
            
            # Store connection
            self.active_connections[session_id] = websocket
            
            # Initialize conversation context
            context = ConversationContext(
                client_id=client_id,
                conversation_id=session_id,
                language=language
            )
            self.conversation_contexts[session_id] = context
            
            # Send welcome message
            welcome_msg = WebSocketMessage(
                type="connected",
                data={"message": "Connected to chat", "session_id": session_id},
                message_id=str(uuid.uuid4())
            )
            await self.send_message(websocket, welcome_msg)
            
            logger.info(f"WebSocket connected: {session_id} for client {client_id}")
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close(code=1000)
    
    async def disconnect(self, session_id: str):
        """Handle WebSocket disconnection."""
        try:
            # Clean up connection
            if session_id in self.active_connections:
                del self.active_connections[session_id]
            
            # Clean up conversation context
            if session_id in self.conversation_contexts:
                del self.conversation_contexts[session_id]
            
            # Clean up chat agent session
            chat_agent.cleanup_session(session_id)
            
            logger.info(f"WebSocket disconnected: {session_id}")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def receive_message(self, websocket: WebSocket, session_id: str):
        """Receive and process incoming messages."""
        try:
            # Receive message
            data = await websocket.receive_text()
            
            # Log raw message for debugging
            logger.debug(f"Raw WebSocket message received: {data[:200]}...")
            
            # Parse message
            try:
                ws_message = WebSocketMessage.model_validate_json(data)
                logger.debug(f"Parsed WebSocket message: type={ws_message.type}, data_type={type(ws_message.data)}")
            except Exception as e:
                logger.warning(f"Invalid message format: {e}")
                logger.warning(f"Raw data: {data[:500]}")
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": "Invalid message format"},
                    message_id=str(uuid.uuid4())
                )
                await self.send_message(websocket, error_msg)
                return
            
            # Process based on message type
            if ws_message.type == "request":
                await self._handle_chat_request(websocket, session_id, ws_message)
            elif ws_message.type == "ping":
                await self._handle_ping(websocket, ws_message)
            else:
                logger.warning(f"Unknown message type: {ws_message.type}")
                
        except WebSocketDisconnect:
            await self.disconnect(session_id)
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            try:
                error_msg = WebSocketMessage(
                    type="error",
                    data={"error": "Internal server error"},
                    message_id=str(uuid.uuid4())
                )
                await self.send_message(websocket, error_msg)
            except:
                pass
    
    async def _handle_chat_request(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        ws_message: WebSocketMessage
    ):
        """Handle incoming chat request."""
        try:
            if not ws_message.data:
                raise ValueError("No data in request")
            
            # Parse chat request
            try:
                if isinstance(ws_message.data, dict):
                    # Validate required fields
                    if 'media_type' not in ws_message.data:
                        raise ValueError("Missing required field: media_type")
                    if 'content' not in ws_message.data:
                        raise ValueError("Missing required field: content")
                    
                    chat_request = ChatRequest.model_validate(ws_message.data)
                else:
                    chat_request = ws_message.data
                
                logger.debug(f"ChatRequest parsed: media_type={chat_request.media_type}, mime_type={chat_request.mime_type}")
                
            except Exception as e:
                logger.error(f"Failed to parse ChatRequest: {e}")
                logger.error(f"Data: {ws_message.data}")
                raise ValueError(f"Invalid chat request format: {e}")
            
            # Get conversation context
            context = self.conversation_contexts.get(session_id)
            if not context:
                raise ValueError("No conversation context found")
            
            # Log the incoming request for debugging
            logger.info(f"Processing {chat_request.media_type} request for session {session_id}")
            if chat_request.media_type == MediaType.IMAGE:
                logger.info(f"Image request - MIME type: {chat_request.mime_type}, Content length: {len(chat_request.content)}")
                logger.debug(f"Image content preview: {chat_request.content[:100]}...")
            
            # Add user message to context
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                conversation_id=session_id,
                client_id=context.client_id,
                role="user",
                media_type=chat_request.media_type,
                content=chat_request.content,
                mime_type=chat_request.mime_type,
                metadata=chat_request.metadata
            )
            context.recent_messages.append(user_message)
            
            # Keep only recent messages
            if len(context.recent_messages) > context.max_context_messages:
                context.recent_messages = context.recent_messages[-context.max_context_messages:]
            
            # Process with AI agent
            logger.info(f"Processing {chat_request.media_type} request for session {session_id}")
            try:
                response = await chat_agent.process_message(chat_request, context)
                logger.info(f"AI agent response received: {len(response.text)} characters")
            except Exception as agent_error:
                logger.error(f"AI agent processing failed: {agent_error}")
                raise agent_error
            
            # Add AI response to context
            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                conversation_id=session_id,
                client_id=context.client_id,
                role="assistant",
                media_type=MediaType.TEXT,
                content=response.text,
                metadata=response.metadata
            )
            context.recent_messages.append(ai_message)
            
            # Send response
            response_msg = WebSocketMessage(
                type="response",
                data=response,
                message_id=str(uuid.uuid4())
            )
            await self.send_message(websocket, response_msg)
            
            logger.info(f"Response sent for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling chat request: {e}")
            error_msg = WebSocketMessage(
                type="error",
                data={"error": str(e)},
                message_id=str(uuid.uuid4())
            )
            await self.send_message(websocket, error_msg)
    
    async def _handle_ping(self, websocket: WebSocket, ws_message: WebSocketMessage):
        """Handle ping message."""
        try:
            pong_msg = WebSocketMessage(
                type="pong",
                data={"timestamp": datetime.utcnow().isoformat()},
                message_id=ws_message.message_id
            )
            await self.send_message(websocket, pong_msg)
        except Exception as e:
            logger.warning(f"Error handling ping: {e}")
    
    async def send_message(self, websocket: WebSocket, message: WebSocketMessage):
        """Send message to WebSocket client."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_message(self, message: WebSocketMessage, exclude_session: Optional[str] = None):
        """Broadcast message to all connected clients."""
        disconnected_sessions = []
        
        for session_id, websocket in self.active_connections.items():
            if session_id != exclude_session:
                try:
                    await self.send_message(websocket, message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {session_id}: {e}")
                    disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            await self.disconnect(session_id)


# Global WebSocket manager
chat_websocket = ChatWebSocket()
