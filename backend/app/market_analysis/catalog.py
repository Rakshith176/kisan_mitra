from __future__ import annotations

from .nearest_markets import Mandi


# Temporary static mandi catalog (replace with DB or official list later)
MANDI_CATALOG: list[Mandi] = [
    Mandi(name="KR Market, Bengaluru", lat=12.9650, lon=77.5800, district="Bengaluru Urban", state="Karnataka"),
    Mandi(name="Yeshwanthpur APMC", lat=13.0280, lon=77.5400, district="Bengaluru Urban", state="Karnataka"),
    Mandi(name="Tumakuru APMC", lat=13.3409, lon=77.1010, district="Tumakuru", state="Karnataka"),
    Mandi(name="Mysuru APMC", lat=12.2958, lon=76.6394, district="Mysuru", state="Karnataka"),
]


