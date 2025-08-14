from collections import defaultdict
_QUEUES = defaultdict(list)

def handle(msisdn: str, intent: str, ent: dict) -> dict:
    svc = ent.get("service") or "clinic"
    loc = ent.get("location") or "Unknown"
    key = f"{svc}:{loc}"
    if intent == "queue_join":
        _QUEUES[key].append(msisdn)
        pos = len(_QUEUES[key])
        return {"user_friendly_text": f"Joined {svc} queue at {loc}. Your position: {pos}."}
    if intent == "queue_status":
        try:
            pos = _QUEUES[key].index(msisdn) + 1
            return {"user_friendly_text": f"Your position in {svc} at {loc}: {pos}."}
        except ValueError:
            return {"user_friendly_text": f"You're not in the {svc} queue at {loc}."}
    return {"user_friendly_text": "Queue action not recognized."}
