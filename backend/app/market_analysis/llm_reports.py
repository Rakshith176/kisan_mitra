from __future__ import annotations

from typing import Dict, List, Tuple

from llama_index.core import PromptTemplate
from llama_index.llms.gemini import Gemini

from ..config import settings


SUMMARY_PROMPT = PromptTemplate(
    (
        "You are an agriculture market advisor.\n"
        "Given top mandi prices and distances for a crop, write a short actionable summary.\n"
        "Respond in {language}. Keep it 2-3 concise sentences, farmer-friendly.\n"
        "Inputs: {inputs_json}"
    )
)


RECOMMENDATIONS_PROMPT = PromptTemplate(
    (
        "You are an agriculture advisor.\n"
        "Based on these mandi options (with distance and price), provide 2-3 bullet recommendations.\n"
        "Respond in {language}. Keep bullets short and actionable.\n"
        "Inputs: {inputs_json}"
    )
)


def _llm() -> Gemini:
    return Gemini(api_key=settings.google_api_key or "", model=settings.gemini_model)


async def generate_multilingual_analysis(inputs_json: str) -> Dict[str, Tuple[str, List[str]]]:
    llm = _llm()
    results: Dict[str, Tuple[str, List[str]]] = {}
    for language in ("en", "hi", "kn"):
        summary = (await llm.acomplete(SUMMARY_PROMPT.format(language=language, inputs_json=inputs_json))).text or ""
        recs_text = (await llm.acomplete(RECOMMENDATIONS_PROMPT.format(language=language, inputs_json=inputs_json))).text or ""
        # Split bullets roughly; frontend can render better
        recs = [line.strip("- ") for line in recs_text.splitlines() if line.strip()][:3]
        results[language] = (summary.strip(), recs)
    return results


