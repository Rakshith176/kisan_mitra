from __future__ import annotations

from typing import Protocol

from ..schemas import FeedCard
from .context import FeedContext


class CardGenerator(Protocol):
    async def generate(self, ctx: FeedContext) -> list[FeedCard]:  # pragma: no cover - type contract
        ...


