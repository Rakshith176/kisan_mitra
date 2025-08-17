from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
from google.generativeai.types import Content, Part, Blob
from google.generativeai.types.generation_types import GenerateContentResponse

from ..config import settings
from ..db import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Conversation, ChatMessage, User

router = APIRouter()
logger = logging.getLogger(__name__)

# Configure Google Generative AI
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)

class WebSocketManager:
    """Manages WebSocket connections and Google ADK integration"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_states: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_states[session_id] = {
            "assistant_text": "",
            "assistant_audio_chunks": [],
            "turn_started_at": None,
            "is_connected": True
        }
        logger.info(f"WebSocket connected for session: {session_id}")
        
    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.connection_states:
            del self.connection_states[session_id]
        logger.info(f"WebSocket disconnected for session: {session_id}")
        
    async def send_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Safely send a message to a specific WebSocket connection"""
        if session_id not in self.active_connections:
            return False
            
        try:
            websocket = self.active_connections[session_id]
            json_message = json.dumps(message)
            
            # Validate message size
            if len(json_message) > 100000:  # 100KB limit
                logger.warning(f"Message too large: {len(json_message)} chars")
                return False
                
            await websocket.send_text(json_message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to session {session_id}: {e}")
            return False

# Global WebSocket manager
ws_manager = WebSocketManager()

async def start_gemini_session(user_id: str, language: str = "en") -> Dict[str, Any]:
    """Start a Gemini session for live conversation"""
    try:
        # Initialize Gemini model for live conversation
        model = genai.GenerativeModel(settings.gemini_live_model)
        
        # Create conversation context
        context = f"""
        You are a live agricultural advisory assistant for smallholder farmers in India.
        Language preference: {language}
        User ID: {user_id}
        
        Requirements:
        - Always reply with BOTH: (1) a concise, farmer-friendly text answer and (2) a spoken audio answer
        - Prefer the user's language if known (en/hi/kn). If unsure, default to English.
        - Keep answers short, actionable, and avoid brand-specific chemicals.
        - If the user sends an image (e.g., crop/leaf), briefly describe what you see and incorporate it into advice.
        - If the user sends audio, transcribe and answer; include key actions and reasons.
        - If you are uncertain, ask a brief clarifying question before giving detailed steps.
        """
        
        # Start chat session
        chat = model.start_chat(history=[])
        
        return {
            "model": model,
            "chat": chat,
            "context": context,
            "language": language
        }
    except Exception as e:
        logger.error(f"Failed to start Gemini session: {e}")
        raise

async def process_gemini_response(
    response: GenerateContentResponse, 
    session_id: str, 
    state: Dict[str, Any]
) -> None:
    """Process Gemini response and send to WebSocket client"""
    try:
        if not response.text:
            return
            
        # Track turn start time
        if state.get("turn_started_at") is None:
            state["turn_started_at"] = datetime.utcnow()
            
        # Send partial text
        text_message = {
            "mime_type": "text/plain",
            "data": response.text,
            "partial": True
        }
        
        if not await ws_manager.send_message(session_id, text_message):
            logger.error(f"Failed to send partial text for session {session_id}")
            return
            
        # Accumulate text
        state["assistant_text"] = (state.get("assistant_text") or "") + response.text
        
        # Send turn complete marker
        turn_message = {
            "turn_complete": True,
            "interrupted": False
        }
        
        if not await ws_manager.send_message(session_id, turn_message):
            logger.error(f"Failed to send turn complete for session {session_id}")
            
    except Exception as e:
        logger.error(f"Error processing Gemini response: {e}")

async def agent_to_client_messaging(websocket: WebSocket, session_id: str, state: Dict[str, Any]):
    """Handle agent responses and send to client"""
    try:
        while state.get("is_connected", False):
            # This will be implemented with actual Gemini streaming
            # For now, we'll handle it in the main WebSocket loop
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Agent to client messaging error: {e}")
    finally:
        state["is_connected"] = False

async def client_to_agent_messaging(
    websocket: WebSocket, 
    session_id: str, 
    gemini_session: Dict[str, Any], 
    state: Dict[str, Any]
):
    """Handle client messages and send to Gemini agent"""
    try:
        while state.get("is_connected", False):
            try:
                message_json = await websocket.receive_text()
                if not message_json:
                    continue
                    
                # Validate JSON message length
                if len(message_json) > 50000:  # 50KB limit
                    error_message = {
                        "error": {
                            "code": "message_too_large", 
                            "message": "Message exceeds size limit"
                        }
                    }
                    await ws_manager.send_message(session_id, error_message)
                    continue
                    
                message = json.loads(message_json)
                mime_type = message.get("mime_type")
                data = message.get("data")
                
                if not mime_type or not data:
                    error_message = {
                        "error": {
                            "code": "invalid_format", 
                            "message": "Missing mime_type or data"
                        }
                    }
                    await ws_manager.send_message(session_id, error_message)
                    continue

                if mime_type == "text/plain":
                    if not isinstance(data, str):
                        error_message = {
                            "error": {
                                "code": "invalid_data_type", 
                                "message": "Text data must be a string"
                            }
                        }
                        await ws_manager.send_message(session_id, error_message)
                        continue
                        
                    # Validate text length
                    if len(data) > 10000:  # 10KB limit
                        error_message = {
                            "error": {
                                "code": "text_too_long", 
                                "message": "Text exceeds length limit"
                            }
                        }
                        await ws_manager.send_message(session_id, error_message)
                        continue
                        
                    # Send to Gemini
                    try:
                        chat = gemini_session["chat"]
                        response = await chat.send_message_async(data)
                        await process_gemini_response(response, session_id, state)
                        
                        # Persist user message
                        await persist_user_message(state, kind="text", text=data, mime_type="text/plain")
                        
                    except Exception as e:
                        logger.error(f"Failed to process text with Gemini: {e}")
                        error_message = {
                            "error": {
                                "code": "gemini_error", 
                                "message": "Failed to process message"
                            }
                        }
                        await ws_manager.send_message(session_id, error_message)
                    continue

                if mime_type.startswith("audio/pcm") or mime_type in ("image/jpeg", "image/png"):
                    try:
                        # Validate base64 data
                        if not isinstance(data, str):
                            error_message = {
                                "error": {
                                    "code": "invalid_data_type", 
                                    "message": "Media data must be base64 string"
                                }
                            }
                            await ws_manager.send_message(session_id, error_message)
                            continue
                            
                        decoded_data = base64.b64decode(data)
                        
                        # Enforce size caps
                        max_bytes = 2 * 1024 * 1024 if mime_type.startswith("audio/pcm") else 1 * 1024 * 1024
                        if len(decoded_data) > max_bytes:
                            error_message = {
                                "error": {
                                    "code": "payload_too_large", 
                                    "message": f"{mime_type} exceeds size limit"
                                }
                            }
                            await ws_manager.send_message(session_id, error_message)
                            continue
                            
                        # Persist user media
                        if mime_type.startswith("audio/pcm"):
                            await persist_user_message(state, kind="audio", blob=decoded_data, mime_type=mime_type)
                        else:
                            await persist_user_message(state, kind="image", blob=decoded_data, mime_type=mime_type)
                            
                        # Send to Gemini with media
                        try:
                            chat = gemini_session["chat"]
                            if mime_type.startswith("audio/pcm"):
                                # For audio, we'll need to implement transcription first
                                # For now, acknowledge receipt
                                await ws_manager.send_message(session_id, {
                                    "mime_type": "text/plain",
                                    "data": "Audio received, processing...",
                                    "partial": True
                                })
                            else:
                                # For images, send to Gemini
                                response = await chat.send_message_async([
                                    "Please analyze this image and provide agricultural advice:",
                                    Blob(data=decoded_data, mime_type=mime_type)
                                ])
                                await process_gemini_response(response, session_id, state)
                                
                        except Exception as e:
                            logger.error(f"Failed to process media with Gemini: {e}")
                            error_message = {
                                "error": {
                                    "code": "gemini_error", 
                                    "message": "Failed to process media"
                                }
                            }
                            await ws_manager.send_message(session_id, error_message)
                            
                    except Exception as e:
                        logger.error(f"Failed to process media message: {e}")
                        error_message = {
                            "error": {
                                "code": "media_processing_error", 
                                "message": "Failed to process media"
                            }
                        }
                        await ws_manager.send_message(session_id, error_message)
                        continue

                # Unsupported mime type
                error_message = {
                    "error": {
                        "code": "unsupported_mime_type", 
                        "message": f"Unsupported mime type: {mime_type}"
                    }
                }
                await ws_manager.send_message(session_id, error_message)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in message: {e}")
                error_message = {
                    "error": {
                        "code": "invalid_json", 
                        "message": "Invalid JSON format"
                    }
                }
                await ws_manager.send_message(session_id, error_message)
            except Exception as e:
                logger.error(f"Error processing client message: {e}")
                error_message = {
                    "error": {
                        "code": "processing_error", 
                        "message": "Failed to process message"
                    }
                }
                await ws_manager.send_message(session_id, error_message)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        state["is_connected"] = False
    except Exception as e:
        logger.error(f"Client to agent messaging error: {e}")
        state["is_connected"] = False

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for live chat with Gemini"""
    gemini_session = None
    agent_to_client_task = None
    client_to_agent_task = None
    
    try:
        # Parse query parameters
        qs = websocket.url.query or ""
        from urllib.parse import parse_qs

        params = parse_qs(qs)
        client_id = params.get("clientId", ["anonymous"])[0]
        language = params.get("language", ["en"])[0]
        conversation_id = params.get("conversationId", [None])[0]

        if not conversation_id:
            await websocket.send_text(json.dumps({
                "error": {
                    "code": "missing_conversation_id", 
                    "message": "conversationId is required"
                }
            }))
            await websocket.close()
            return

        # Ensure conversation & user exist
        try:
            async with AsyncSessionLocal() as db:
                await ensure_user_and_conversation(db, client_id=client_id, conversation_id=conversation_id, language=language)
        except Exception as e:
            logger.error(f"Failed to ensure user and conversation: {e}")
            await websocket.send_text(json.dumps({
                "error": {
                    "code": "database_error", 
                    "message": "Failed to setup conversation"
                }
            }))
            await websocket.close()
            return

        # Start Gemini session
        try:
            gemini_session = await start_gemini_session(client_id, language=language)
        except Exception as e:
            logger.error(f"Failed to start Gemini session: {e}")
            await websocket.send_text(json.dumps({
                "error": {
                    "code": "gemini_startup_error", 
                    "message": "Failed to start AI assistant"
                }
            }))
            await websocket.close()
            return

        # Connect WebSocket
        await ws_manager.connect(websocket, session_id)
        
        # Connection state
        state: dict = {
            "client_id": client_id,
            "conversation_id": conversation_id,
            "language": language,
            "assistant_text": "",
            "assistant_audio_chunks": [],
            "turn_started_at": None,
            "is_connected": True,
        }

        # Seed context with recent messages
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.conversation_id == conversation_id, ChatMessage.type == "text")
                    .order_by(ChatMessage.created_at.desc())
                    .limit(5)
                )
                rows = list(reversed(result.scalars().all()))
                for msg in rows:
                    if msg.text and isinstance(msg.text, str):
                        # Send context to Gemini
                        try:
                            chat = gemini_session["chat"]
                            await chat.send_message_async(f"Context: {msg.role}: {msg.text}")
                        except Exception as e:
                            logger.warning(f"Failed to seed context message: {e}")
        except Exception as e:
            logger.warning(f"Failed to seed context: {e}")

        # Start messaging tasks
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, session_id, state)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, session_id, gemini_session, state)
        )

        # Wait for tasks to complete
        done, pending = await asyncio.wait(
            [agent_to_client_task, client_to_agent_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "error": {
                    "code": "websocket_error", 
                    "message": "Internal server error"
                }
            }))
        except Exception:
            pass
    finally:
        # Cleanup
        try:
            if gemini_session and "chat" in gemini_session:
                gemini_session["chat"].close()
        except Exception as e:
            logger.error(f"Error closing Gemini session: {e}")
            
        if agent_to_client_task and not agent_to_client_task.done():
            agent_to_client_task.cancel()
        if client_to_agent_task and not client_to_agent_task.done():
            client_to_agent_task.cancel()
            
        await ws_manager.disconnect(session_id)
        
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")

@router.get("/ws-info", tags=["chat"])
async def ws_info(request: Request) -> dict:
    """HTTP docs helper for the Live WS endpoint"""
    return {
        "path": "/chat/ws/{session_id}",
        "query": {
            "clientId": "<string>",
            "language": "en|hi|kn",
            "conversationId": "<string>",
        },
        "send_frames": [
            {"mime_type": "text/plain", "data": "Hello"},
            {"mime_type": "audio/pcm", "data": "<base64 16k mono>"},
            {"mime_type": "image/jpeg", "data": "<base64>"},
            {"mime_type": "image/png", "data": "<base64>"},
        ],
        "receive_frames": [
            {"mime_type": "text/plain", "data": "partial text", "partial": True},
            {"mime_type": "text/plain", "data": "final text"},
            {"turn_complete": True, "interrupted": False},
        ],
    }

# Helper functions
async def ensure_user_and_conversation(db: AsyncSession, *, client_id: str, conversation_id: str, language: str) -> None:
    """Ensure user and conversation exist and belong together"""
    user = await db.get(User, client_id)
    if user is None:
        user = User(client_id=client_id, language=language)
        db.add(user)
        await db.commit()
        
    convo = await db.get(Conversation, conversation_id)
    if convo is None:
        convo = Conversation(id=conversation_id, client_id=client_id, language=language)
        db.add(convo)
        await db.commit()
    elif convo.client_id != client_id:
        raise WebSocketDisconnect(code=1008)

def _media_dir() -> Path:
    """Get media directory path"""
    base = Path(__file__).resolve().parents[2] / "data" / "media"
    (base / "audio").mkdir(parents=True, exist_ok=True)
    (base / "images").mkdir(parents=True, exist_ok=True)
    return base

async def persist_user_message(
    state: dict,
    *,
    kind: str,
    text: Optional[str] = None,
    blob: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> None:
    """Persist user message to database"""
    async with AsyncSessionLocal() as db:
        media_path: Optional[str] = None
        if kind == "audio" and blob is not None:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
            audio_path = _media_dir() / "audio" / f"{state['conversation_id']}_{ts}.pcm"
            audio_path.write_bytes(blob)
            media_path = str(audio_path)
        elif kind == "image" and blob is not None and mime_type in ("image/jpeg", "image/png"):
            ext = ".jpg" if mime_type == "image/jpeg" else ".png"
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
            img_path = _media_dir() / "images" / f"{state['conversation_id']}_{ts}{ext}"
            img_path.write_bytes(blob)
            media_path = str(img_path)

        msg = ChatMessage(
            id=f"msg_{datetime.utcnow().timestamp()}_{kind}",
            conversation_id=state["conversation_id"],
            client_id=state["client_id"],
            role="user",
            type=kind,
            text=text,
            mime_type=mime_type,
            audio_path=media_path if kind == "audio" else None,
            image_path=media_path if kind == "image" else None,
        )
        db.add(msg)
        convo = await db.get(Conversation, state["conversation_id"])
        if convo:
            convo.updated_at = datetime.utcnow()
        await db.commit()

async def persist_assistant_message(state: dict) -> None:
    """Persist assistant message to database"""
    text = (state.get("assistant_text") or "").strip()
    audio_chunks: list[bytes] = state.get("assistant_audio_chunks") or []
    latency_ms = 0
    
    if state.get("turn_started_at"):
        latency_ms = int((datetime.utcnow() - state["turn_started_at"]).total_seconds() * 1000)

    audio_path: Optional[str] = None
    if audio_chunks:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
        audio_file = _media_dir() / "audio" / f"{state['conversation_id']}_{ts}_ai.pcm"
        audio_file.write_bytes(b"".join(audio_chunks))
        audio_path = str(audio_file)

    async with AsyncSessionLocal() as db:
        msg = ChatMessage(
            id=f"msg_{datetime.utcnow().timestamp()}_assistant",
            conversation_id=state["conversation_id"],
            client_id=state["client_id"],
            role="assistant",
            type="text",
            text=text or None,
            mime_type="text/plain" if text else None,
            audio_path=audio_path,
            tokens_input=0,
            tokens_output=0,
            latency_ms=latency_ms,
        )
        db.add(msg)
        convo = await db.get(Conversation, state["conversation_id"])
        if convo:
            convo.updated_at = datetime.utcnow()
        await db.commit()


