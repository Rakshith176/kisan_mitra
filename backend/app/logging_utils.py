from __future__ import annotations

import logging
import os


def configure_logging(level: str = "INFO") -> None:
    level_name = level.upper()
    numeric_level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    # Reduce noisy libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


