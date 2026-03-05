from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.course_service import CourseService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = CourseService(db)
    results = svc.search(q) if q.strip() else []
    return templates.TemplateResponse("search/results.html", {
        "request": request,
        "current_user": current_user,
        "query": q,
        "results": results,
    })
