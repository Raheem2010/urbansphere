from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers.webhook import router as webhook_router
from src.services import watsonx_client  

app = FastAPI(title="UrbanSphere MVP")

# --- Resolve paths relative to this file (src/) ---
BASE_DIR = Path(__file__).resolve().parent        
TEMPLATES_DIR = BASE_DIR / "templates"             
STATIC_DIR = BASE_DIR / "static"                    

# Ensure templates dir exists so TemplateResponse won't blow up later
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Only mount /static if the folder actually exists (avoids RuntimeError)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Routers
app.include_router(webhook_router)  

@app.on_event("startup")
def _warm_up():
    # Pre-build client/model so the first user call is fast
    watsonx_client.health_check()

# Minimal dashboard (demo-friendly)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, cdn: str = Query(default="play")):
    use_link = (cdn.lower() == "link")
    counts = dict(waste_count=2, queue_count=1, property_count=3)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "use_link": use_link, **counts},
    )

# Convenience redirect
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/dashboard")

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}
