from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Optional

from .schemas import MandiPriceRow, RankedMandiPrice


@dataclass
class PriceRankingConfig:
    weight_modal: float = 1.0
    weight_distance: float = 0.2  # per 10km penalty
    weight_arrivals: float = 0.1


def _score(row: RankedMandiPrice, cfg: PriceRankingConfig) -> float:
    distance_penalty = cfg.weight_distance * (row.distance_km / 10.0)
    arrivals_bonus = cfg.weight_arrivals * (row.arrivals or 0.0) / 1000.0
    return cfg.weight_modal * row.modal - distance_penalty + arrivals_bonus


def rank_prices(
    *,
    rows: Iterable[RankedMandiPrice],
    cfg: Optional[PriceRankingConfig] = None,
) -> List[RankedMandiPrice]:
    cfg = cfg or PriceRankingConfig()
    return sorted(rows, key=lambda r: _score(r, cfg), reverse=True)


def normalize_to_ranked(
    *,
    raw: Iterable[MandiPriceRow],
    distances_km: dict[str, float],
) -> List[RankedMandiPrice]:
    ranked: list[RankedMandiPrice] = []
    for r in raw:
        d = distances_km.get(r.market)
        if d is None:
            continue
        ranked.append(
            RankedMandiPrice(
                market=r.market,
                distance_km=d,
                modal=r.modal,
                min_price=r.min_price,
                max_price=r.max_price,
                unit=r.unit,
                arrivals=r.arrivals,
                date=r.date,
            )
        )
    return ranked


