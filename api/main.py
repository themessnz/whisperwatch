from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.routes import router as api_router
from config.manager import config

app = FastAPI(title="WhisperWatch API")

# Mount static files
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

# Templates
templates = Jinja2Templates(directory="ui/templates")

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request, "config": config._config})
