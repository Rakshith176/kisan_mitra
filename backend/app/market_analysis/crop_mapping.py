from __future__ import annotations

from typing import Optional


_ID_TO_COMMODITY: dict[str, str] = {
    "crop_rice": "Rice",
    "crop_wheat": "Wheat",
    "crop_maize": "Maize",
    "crop_millet": "Bajra",
}


def map_crop_to_commodity(*, crop_id: Optional[str], crop_name_en: Optional[str]) -> str:
    if crop_id and crop_id in _ID_TO_COMMODITY:
        return _ID_TO_COMMODITY[crop_id]
    if crop_name_en:
        name = crop_name_en.strip().lower()
        if "rice" in name:
            return "Rice"
        if "wheat" in name:
            return "Wheat"
        if "maize" in name or "corn" in name:
            return "Maize"
        if "millet" in name or "bajra" in name:
            return "Bajra"
    return crop_name_en or ""


