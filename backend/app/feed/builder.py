from __future__ import annotations

from typing import Iterable, List

from .context import FeedContext
from .types import CardGenerator
from ..schemas import FeedCard
import logging


class FeedBuilder:
    def __init__(self, generators: Iterable[CardGenerator]):
        self._generators: list[CardGenerator] = list(generators)

    async def build(self, ctx: FeedContext, limit: int = 20) -> List[FeedCard]:
        cards: list[FeedCard] = []
        for gen in self._generators:
            try:
                logging.getLogger(__name__).info("Running generator: %s", gen.__class__.__name__)
                gen_cards = await gen.generate(ctx)
                logging.getLogger(__name__).info(
                    "Generator %s produced %d cards", gen.__class__.__name__, len(gen_cards)
                )
                cards.extend(gen_cards)
            except Exception:
                logging.getLogger(__name__).exception("Generator %s failed", gen.__class__.__name__)
                # Fail-open per generator to keep others working
                continue
            if len(cards) >= limit:
                break
        # Simple recency sort
        cards.sort(key=lambda c: c.created_at, reverse=True)
        return cards[:limit]


