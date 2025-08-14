import time
from typing import Any, Dict
from src.services.watsonx_client import generate_json

SYSTEM = (
  "You are Brenda, an intent router for a civic assistant handling: "
  "sanita_report (waste), queue_join, queue_status, property_lookup. "
  "Extract entities (location, waste_type, service, property_type, budget, urgency). "
  "Return ONLY valid JSON exactly matching: "
  '{"intent":"...", "confidence":0-1, "entities":{...}, "safety_flags":[], "trace":{"version":"brenda.v1","latency_ms":0}}. '
  "If unsure, set intent='clarify' and include entities.question."
)

def route(text: str) -> Dict[str, Any]:
    t0 = time.time()
    prompt = f"<system>{SYSTEM}</system>\n<user>{text}</user>"
    data = generate_json(prompt)

    # fallback on parse error or missing fields
    if "error" in data:
        data = {
            "intent": "clarify",
            "confidence": 0,
            "entities": {"question": "Do you need waste, queue, or property help?"},
            "safety_flags": [],
            "trace": {"version": "brenda.v1", "latency_ms": 0, "note": "json_parse_failed"},
        }

    data.setdefault("intent", "clarify")
    data.setdefault("entities", {})
    try:
        data["confidence"] = float(data.get("confidence", 0) or 0)
    except Exception:
        data["confidence"] = 0.0

    data.setdefault("trace", {})
    data["trace"]["version"] = "brenda.v1"
    data["trace"]["latency_ms"] = int((time.time() - t0) * 1000)
    return data