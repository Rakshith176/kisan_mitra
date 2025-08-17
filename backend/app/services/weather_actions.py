from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini

from ..config import settings
from ..schemas import WeatherDailyItem, LocalizedText


SYSTEM = (
    "You are a farmer advisor. Provide cheap, safe, brand-agnostic actions. Keep concise."
)

PROMPT = PromptTemplate(
    (
        "Generate weather-action advice for a farmer.\n"
        "Return JSON with keys: title, summary, recommendations (2-3 bullets), risk_tags (array of {{type, severity}}),"
        " action_window_start, action_window_end.\n"
        "Language: {language}.\n"
        "Inputs: crop={crop}, irrigation={irrigation}, soil={soil}, forecast={forecast}."
    )
)


def _llm() -> Gemini:
    return Gemini(api_key=settings.google_api_key or "", model=settings.gemini_model)


def _thresholds(days: List[WeatherDailyItem]) -> Tuple[List[Dict], Tuple[str, str]]:
    tags: List[Dict] = []
    start = days[0].date.isoformat() if days else None
    end = days[min(2, len(days) - 1)].date.isoformat() if days else None
    # Simple thresholds
    if any((d.precipitation_mm or 0) >= 20 for d in days[:3]):
        tags.append({"type": "rain", "severity": "high"})
    if any((d.temp_max_c or 0) >= 35 for d in days[:3]):
        tags.append({"type": "heat", "severity": "med"})
    if any((d.wind_kph or 0) >= 20 for d in days[:3]):
        tags.append({"type": "wind", "severity": "med"})
    return tags, (start or "", end or "")


async def generate_weather_actions(
    *,
    language: str,
    crop: str,
    irrigation: str | None,
    soil: str | None,
    forecast_days: List[WeatherDailyItem],
) -> Tuple[LocalizedText, List[LocalizedText], List[Dict], str | None, str | None]:
    # Deterministic hints
    tags, (start, end) = _thresholds(forecast_days)

    # LLM summary + bullets (multilingual via separate calls for clarity)
    llm = _llm()
    import json

    # Concise JSON context for LLM
    fc = [
        {
            "date": d.date.isoformat(),
            "tmin": d.temp_min_c,
            "tmax": d.temp_max_c,
            "rain_mm": d.precipitation_mm,
            "wind_kph": d.wind_kph,
        }
        for d in forecast_days[:3]
    ]
    inputs = json.dumps({"crop": crop, "irrigation": irrigation, "soil": soil, "forecast_3d": fc, "tags": tags})

    texts: Dict[str, Tuple[str, List[str]]] = {}
    for lang in ("en", "hi", "kn"):
        resp = await llm.acomplete(SYSTEM + "\n\n" + PROMPT.format(language=lang, crop=crop, irrigation=irrigation or "", soil=soil or "", forecast=inputs))
        t = resp.text or "{}"
        try:
            data = json.loads(t)
            title = data.get("title", "Weather advisory")
            summary = data.get("summary", "")
            recs = data.get("recommendations", [])[:3]
        except Exception:
            title = "Weather advisory"
            summary = ""
            recs = []
        texts[lang] = (summary, recs)

    title_text = LocalizedText(en="Weather advisory", hi=None, kn=None)
    analysis_text = LocalizedText(en=texts["en"][0], hi=texts["hi"][0], kn=texts["kn"][0])
    recs = [
        LocalizedText(
            en=texts["en"][1][i] if i < len(texts["en"][1]) else "",
            hi=texts["hi"][1][i] if i < len(texts["hi"][1]) else None,
            kn=texts["kn"][1][i] if i < len(texts["kn"][1]) else None,
        )
        for i in range(min(3, len(texts["en"][1])))
    ]
    return analysis_text, recs, tags, start, end


