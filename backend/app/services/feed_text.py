from __future__ import annotations

from typing import Optional

from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini

from ..config import settings


SYSTEM_PROMPT = (
    "You are an agriculture assistant generating short, clear advisory card texts for farmers. "
    "Respond concisely. Provide up to 2 alternative phrasings per language when asked."
)

WEATHER_CARD_PROMPT = PromptTemplate(
    (
        "Generate localized advisory texts for a weather card.\n"
        "Language: {language} (use English if not supported).\n"
        "Location: lat={lat}, lon={lon}.\n"
        "Forecast (first 3 days): {forecast_summary}.\n"
        "Return exactly a JSON object with keys 'title' and 'variants' (list of 1-2 short strings)."
    )
)


def _make_llm() -> Gemini:
    return Gemini(api_key=settings.google_api_key or "", model=settings.gemini_model)


async def generate_weather_card_texts(
    language: str, lat: float, lon: float, forecast_summary: str
) -> tuple[str, list[str]]:
    llm = _make_llm()
    prompt = WEATHER_CARD_PROMPT.format(
        language=language, lat=lat, lon=lon, forecast_summary=forecast_summary
    )
    # Using a simple completion; caller should handle failure → default strings
    resp = await llm.acomplete(SYSTEM_PROMPT + "\n\n" + prompt)
    text = resp.text or "{}"
    # naive parse to avoid adding strict deps; caller should be robust
    import json

    try:
        data = json.loads(text)
        title = str(data.get("title", "Weather update"))
        variants = [str(v) for v in data.get("variants", [])][:2]
    except Exception:
        title = "Weather update"
        variants = []
    return title, variants


