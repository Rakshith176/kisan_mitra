from __future__ import annotations

import asyncio
import time
from typing import Iterable, List

from .context import FeedContext
from .types import CardGenerator
from ..schemas import FeedCard
from ..db import AsyncSessionLocal
import logging


class FeedBuilder:
	def __init__(self, generators: Iterable[CardGenerator]):
		self._generators: list[CardGenerator] = list(generators)

	async def build(self, ctx: FeedContext, limit: int = 20, timeout_seconds: float = 30.0) -> List[FeedCard]:
		start_time = time.time()
		
		# Run all generators in parallel for better performance
		async def run_generator(gen: CardGenerator) -> List[FeedCard]:
			gen_start_time = time.time()
			try:
				logging.getLogger(__name__).info("Running generator: %s", gen.__class__.__name__)
				
				# Create a separate database session for each generator to avoid concurrency issues
				async with AsyncSessionLocal() as db_session:
					# Create a new context with the separate session
					gen_ctx = FeedContext(
						db=db_session,
						client_id=ctx.client_id,
						language=ctx.language,
						lat=ctx.lat,
						lon=ctx.lon,
						pincode=ctx.pincode,
						crop_ids=ctx.crop_ids,
					)
					
					gen_cards = await gen.generate(gen_ctx)
				
				gen_duration = time.time() - gen_start_time
				logging.getLogger(__name__).info(
					"Generator %s produced %d cards in %.2f seconds", 
					gen.__class__.__name__, len(gen_cards), gen_duration
				)
				return gen_cards
			except Exception:
				gen_duration = time.time() - gen_start_time
				logging.getLogger(__name__).exception(
					"Generator %s failed after %.2f seconds", gen.__class__.__name__, gen_duration
				)
				# Fail-open per generator to keep others working
				return []

		# Execute all generators concurrently with time budget
		tasks: list[asyncio.Task[List[FeedCard]]] = [asyncio.create_task(run_generator(gen)) for gen in self._generators]
		task_to_gen_name = {task: gen.__class__.__name__ for task, gen in zip(tasks, self._generators)}
		
		# Wait up to timeout_seconds for completion, but keep results of completed tasks
		done, pending = await asyncio.wait(tasks, timeout=timeout_seconds)
		if pending:
			logging.getLogger(__name__).warning(
				"Feed generation time budget reached (%.2fs). %d/%d generators still running; cancelling them",
				timeout_seconds,
				len(pending),
				len(tasks),
			)
			for task in pending:
				task.cancel()
			# Ensure all cancellations are processed
			await asyncio.gather(*pending, return_exceptions=True)
		
		# Collect all cards from successful generators (completed tasks only)
		cards: list[FeedCard] = []
		successful_generators = 0
		for task in done:
			try:
				result = task.result()
				cards.extend(result)
				successful_generators += 1
			except Exception:
				gen_name = task_to_gen_name.get(task, "<unknown>")
				logging.getLogger(__name__).exception(
					"Generator %s failed with exception (after completion)", gen_name
				)
				continue
			
		# Simple recency sort
		cards.sort(key=lambda c: c.created_at, reverse=True)
		final_cards = cards[:limit]
		
		total_duration = time.time() - start_time
		logging.getLogger(__name__).info(
			"Feed generation completed in %.2f seconds: %d/%d generators successful, %d cards returned",
			total_duration, successful_generators, len(self._generators), len(final_cards)
		)
		
		return final_cards


