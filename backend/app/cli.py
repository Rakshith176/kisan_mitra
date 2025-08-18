from __future__ import annotations

import asyncio

from sqlmodel import SQLModel

from .db import engine, AsyncSessionLocal
from .seeds import seed_crops


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_crops(session)


if __name__ == "__main__":
    asyncio.run(init_db())


