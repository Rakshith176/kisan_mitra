"""
FastAPI router for chat endpoints.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import JSONResponse

from .websocket import chat_websocket
from .schemas import WebSocketMessage, ChatRequest, ChatResponse, ConversationContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/")
async def chat_root():
    """Root endpoint for chat service."""
    return {
        "service": "chat",
        "status": "running",
        "endpoints": {
            "websocket": "/ws/{session_id}",
            "health": "/health",
            "sessions": "/sessions/{session_id}/status",
            "stats": "/stats"
        }
    }


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    client_id: str = Query(None, description="Client ID for the chat session"),
    clientId: str = Query(None, description="Client ID for the chat session (alternative)"),
    language: str = Query("en", description="Preferred language (en, hi, kn)")
):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        session_id: Unique session identifier
        client_id: Client identifier (snake_case)
        clientId: Client identifier (camelCase, alternative)
        language: Preferred language (en, hi, kn)
    """
    try:
        # Handle both parameter naming conventions
        actual_client_id = client_id or clientId
        if not actual_client_id:
            logger.error(f"Missing client_id parameter for session {session_id}")
            await websocket.close(code=1008, reason="Missing client_id parameter")
            return
        
        # Log connection attempt
        logger.info(f"WebSocket connection attempt: session_id={session_id}, client_id={actual_client_id}, language={language}")
        
        # Validate language
        if language not in ["en", "hi", "kn"]:
            language = "en"
            logger.info(f"Language reset to default: {language}")
        
        # Connect to WebSocket
        await chat_websocket.connect(websocket, session_id, actual_client_id, language)
        
        # Handle messages
        while websocket.client_state.value == 1:  # CONNECTED
            await chat_websocket.receive_message(websocket, session_id)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        await chat_websocket.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        await chat_websocket.disconnect(session_id)


@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    return {
        "status": "healthy",
        "service": "chat",
        "active_connections": len(chat_websocket.active_connections),
        "active_conversations": len(chat_websocket.conversation_contexts)
    }


@router.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get status of a specific chat session."""
    if session_id not in chat_websocket.conversation_contexts:
        raise HTTPException(status_code=404, detail="Session not found")
    
    context = chat_websocket.conversation_contexts[session_id]
    return {
        "session_id": session_id,
        "client_id": context.client_id,
        "language": context.language,
        "message_count": len(context.recent_messages),
        "connected": session_id in chat_websocket.active_connections
    }


@router.delete("/sessions/{session_id}")
async def close_session(session_id: str):
    """Close a specific chat session."""
    if session_id not in chat_websocket.conversation_contexts:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await chat_websocket.disconnect(session_id)
    return {"message": "Session closed successfully"}


@router.get("/stats")
async def get_chat_stats():
    """Get chat service statistics."""
    return {
        "active_connections": len(chat_websocket.active_connections),
        "active_conversations": len(chat_websocket.conversation_contexts),
        "total_sessions_handled": len(chat_websocket.active_connections) + len(chat_websocket.conversation_contexts)
    }


@router.post("/test-image")
async def test_image_processing():
    """Test endpoint to verify image processing capabilities."""
    from .agent import chat_agent
    
    # Check if vision is supported
    vision_supported = getattr(chat_agent, 'supports_vision', False)
    model_name = chat_agent.model.model_name if hasattr(chat_agent.model, 'model_name') else "Unknown"
    
    return {
        "vision_supported": vision_supported,
        "model_name": model_name,
        "status": "Image processing test endpoint available",
        "note": "Use WebSocket endpoint for actual image processing"
    }
