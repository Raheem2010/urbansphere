import json, pathlib
DATA = pathlib.Path("data")

from typing import Dict, Any

def lookup(ent: Dict[str, Any]) -> Dict[str, Any]:
    loc = (ent.get("location") or "").lower()
    budget = ent.get("budget")
    max_rent = None
    if isinstance(budget, str) and any(ch.isdigit() for ch in budget):
        try:
            max_rent = int("".join(ch for ch in budget if ch.isdigit()))
        except Exception:
            pass
    rows = json.loads((DATA / "listings.json").read_text(encoding="utf-8"))
    filt = [r for r in rows if (not loc or r["location"].lower().startswith(loc)) and (max_rent is None or r["monthly_rent"] <= max_rent)]
    top = filt[:5]
    lines = [f'{r["type"].title()} in {r["location"]} - {r["monthly_rent"]} XAF (Contact {r["contact"]})' for r in top] or ["No matches."]
    return {"user_friendly_text": "Top matches:\n" + "\n".join(lines)}
