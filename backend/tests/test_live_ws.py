from __future__ import annotations

import asyncio
import base64
import json
from contextlib import contextmanager
from typing import Any, AsyncGenerator, List, Tuple

import pytest
from starlette.testclient import TestClient

try:
    from app.main import create_app  # type: ignore
    from app.live import ws as live_ws  # type: ignore
except ModuleNotFoundError:
    # Allow running tests from repo root by fixing sys.path to include backend/
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from app.main import create_app  # type: ignore
    from app.live import ws as live_ws  # type: ignore


class _FakeInlineData:
    def __init__(self, mime_type: str, data: bytes) -> None:
        self.mime_type = mime_type
        self.data = data


class _FakePart:
    def __init__(self, text: str | None = None, inline_data: _FakeInlineData | None = None) -> None:
        self.text = text
        self.inline_data = inline_data


class _FakeContent:
    def __init__(self, parts: List[_FakePart]) -> None:
        self.parts = parts


class _FakeEvent:
    def __init__(
        self,
        *,
        content: _FakeContent | None = None,
        partial: bool = False,
        turn_complete: bool = False,
        interrupted: bool = False,
    ) -> None:
        self.content = content
        self.partial = partial
        self.turn_complete = turn_complete
        self.interrupted = interrupted


class _FakeQueue:
    def __init__(self) -> None:
        self.sent: list[tuple[str, Any]] = []

    def send_content(self, *, content: Any) -> None:
        self.sent.append(("content", content))

    def send_realtime(self, blob: Any) -> None:
        self.sent.append(("realtime", blob))

    def close(self) -> None:  # pragma: no cover - just to satisfy interface
        pass


async def _fake_live_events() -> AsyncGenerator[_FakeEvent, None]:
    # Simulate partial text
    yield _FakeEvent(content=_FakeContent(parts=[_FakePart(text="hello ")]), partial=True)
    await asyncio.sleep(0)
    # Final text
    yield _FakeEvent(content=_FakeContent(parts=[_FakePart(text="hello world")]), partial=False)
    await asyncio.sleep(0)
    # Audio chunk
    audio_bytes = b"\x00\x01\x02\x03"
    yield _FakeEvent(
        content=_FakeContent(parts=[_FakePart(inline_data=_FakeInlineData("audio/pcm", audio_bytes))])
    )
    await asyncio.sleep(0)
    # Turn complete
    yield _FakeEvent(turn_complete=True)


async def _fake_start_agent_session(user_id: str, language: str = "en", response_modalities: List[str] | None = None):
    fake_queue = _FakeQueue()
    return _fake_live_events(), fake_queue


@contextmanager
def _patched_start():
    original = live_ws.start_agent_session
    live_ws.start_agent_session = _fake_start_agent_session  # type: ignore[assignment]
    try:
        yield
    finally:
        live_ws.start_agent_session = original  # type: ignore[assignment]


def test_live_ws_streams_audio_and_text():
    app = create_app()
    with _patched_start():
        client = TestClient(app)
        # Create a test user and conversation first
        from app.models import User, Conversation
        from app.db import AsyncSessionLocal
        import asyncio
        import time
        
        # Use timestamp to ensure unique IDs
        timestamp = str(int(time.time()))
        test_user_id = f"c1_{timestamp}"
        test_conversation_id = f"test_conv_{timestamp}"
        
        async def setup_test_data():
            async with AsyncSessionLocal() as db:
                # Create test user
                user = User(client_id=test_user_id, language="en")
                db.add(user)
                
                # Create test conversation
                conversation = Conversation(
                    id=test_conversation_id,
                    client_id=test_user_id,
                    language="en"
                )
                db.add(conversation)
                await db.commit()
        
        # Run the async setup
        asyncio.run(setup_test_data())
        
        with client.websocket_connect(f"/chat/ws/test_session?clientId={test_user_id}&conversationId={test_conversation_id}&language=en") as ws:
            # Send a user text frame
            ws.send_text(json.dumps({"mime_type": "text/plain", "data": "Hi"}))

            got_final_text = False
            got_audio = False
            got_turn_complete = False
            # Receive up to 5 frames
            for _ in range(5):
                data = ws.receive_text()
                msg = json.loads(data)
                if msg.get("mime_type") == "text/plain" and msg.get("final"):
                    got_final_text = True
                if msg.get("mime_type", "").startswith("audio/pcm"):
                    # Validate base64 decodes
                    base64.b64decode(msg["data"])  # will raise on invalid
                    got_audio = True
                if "turn_complete" in msg:
                    got_turn_complete = True
                if got_final_text and got_audio and got_turn_complete:
                    break

            assert got_final_text, "expected a final text frame"
            assert got_audio, "expected at least one audio chunk"
            assert got_turn_complete, "expected a turn_complete marker"


