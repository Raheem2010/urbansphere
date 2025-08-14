import json, pathlib, datetime as dt
from typing import Any

DATA = pathlib.Path("data")

from typing import Union

def _load(name: str) -> Union[dict[str, Any], list[dict[str, Any]]]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def handle_report(msisdn: str, ent: dict[str, Any]) -> dict[str, Any]:
    routes = _load("collection_routes.json")
    loc_val = ent.get("location") if ent else None
    loc = (str(loc_val) if loc_val is not None else "").strip() or "Unknown"
    route = [r for r in routes if isinstance(r, dict) and "location" in r and isinstance(r["location"], str) and r["location"].lower() == loc.lower()]
    hs = [h for h in _load("waste_hotspots.json") if isinstance(h, dict) and isinstance(h.get("location"), str) and h["location"].lower() == loc.lower()]
    route = [r for r in _load("collection_routes.json") if isinstance(r, dict) and isinstance(r.get("location"), str) and r["location"].lower() == loc.lower()]
    eta = "Next collection window"
    if route:
        eta = "2–4h" if "09:00" in route[0]["daily_windows"] else "4–6h"
    ref = f"SAN-{int(dt.datetime.now(dt.timezone.utc).timestamp())}"
    return {
        "user_friendly_text": f"Thanks! Logged an overflow report for {loc}. Pickup ETA: {eta}. Ref: {ref}",
        "card": {"title":"Waste Report","fields":[["Location",loc],["ETA",eta],["Ref",ref]]},
        "next_actions": ["Check status","Report another","Recycling tips"]
    }
