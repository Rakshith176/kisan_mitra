from __future__ import annotations

import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Ensure API key is set
if not settings.google_api_key:
    logger.error("GOOGLE_API_KEY is not set")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

logger.info(f"Google API key configured successfully")
logger.info(f"Gemini Live model: {settings.gemini_live_model}")

# Note: The actual agent implementation is now handled in ws.py using google.generativeai
# This file is kept for future extensions and configuration


