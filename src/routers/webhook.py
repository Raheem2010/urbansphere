# routers/webhook.py
from fastapi import APIRouter, Request
from src.services.brenda import route as brenda_route
from src.services import waste, queue as queue_agent, realestate
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/webhook")

async def webhook(req: Request) -> JSONResponse:
    ctype = req.headers.get("content-type", "")
    if "application/json" in ctype:
        body = await req.json()
        text = body.get("message_text") or body.get("Body") or ""
        msisdn = body.get("from") or body.get("From") or "anon"
    else:
        form = await req.form()
        text = form.get("Body") or form.get("message_text") or ""
        msisdn = form.get("From") or form.get("from") or "anon"

    routed = brenda_route(text)
    intent = routed.get("intent")
    ent = routed.get("entities", {})

    if intent == "sanita_report":
        reply = waste.handle_report(msisdn, ent)
    elif intent in ("queue_join", "queue_status"):
        reply = queue_agent.handle(msisdn, intent, ent)
    elif intent == "property_lookup":
        reply = realestate.lookup(ent)
    else:
        reply = {"user_friendly_text": "Do you want waste, queue, or property help?"}

    # Twilio expects 200 OK quickly
    return JSONResponse(reply)
