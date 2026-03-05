from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.services.auth_service import AuthService
from app.auth import create_session_token, get_current_user
from config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
limiter = Limiter(key_func=get_remote_address)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # If already logged in, redirect to dashboard
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if token:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    user, error = service.authenticate(email, password)

    if error:
        return templates.TemplateResponse(
            "auth/login.html", {"request": request, "error": error}, status_code=400
        )

    token = create_session_token(user.id)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response
