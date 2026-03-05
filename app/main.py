from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from app.database import engine, Base
import app.models  # noqa — ensures all models are registered before create_all

# Import all routes
from app.routes import auth, dashboard, courses, files, search

# ── Create tables (Alembic handles migrations; this is a safety net) ─────────
Base.metadata.create_all(bind=engine)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title=settings.APP_NAME, docs_url=None, redoc_url=None)  # hide API docs in prod

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(courses.router)
app.include_router(files.router)
app.include_router(search.router)

# ── Error pages ───────────────────────────────────────────────────────────────
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    return templates.TemplateResponse("errors/403.html", {"request": request}, status_code=403)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)


@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return templates.TemplateResponse("errors/429.html", {"request": request}, status_code=429)
