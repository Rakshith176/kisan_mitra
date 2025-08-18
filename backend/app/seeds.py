from __future__ import annotations

from sqlmodel import select

from .models import Crop


DEFAULT_CROPS: list[tuple[str, str, str | None, str | None]] = [
    ("crop_rice", "Rice", "चावल", "ಅಕ್ಕಿ"),
    ("crop_wheat", "Wheat", "गेहूँ", "ಗೋಧಿ"),
    ("crop_maize", "Maize", "मक्का", "ಜೋಳ"),
    ("crop_millet", "Millet", "बाजरा", "ಸಜ್ಜೆ"),
]


async def seed_crops(session) -> None:
    result = await session.execute(select(Crop))
    if result.scalars().first() is not None:
        return
    for cid, en, hi, kn in DEFAULT_CROPS:
        session.add(Crop(id=cid, name_en=en, name_hi=hi, name_kn=kn))
    await session.commit()


