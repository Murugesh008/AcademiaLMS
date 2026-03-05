from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, require_professor
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.file_repository import FileRepository
from app.services.course_service import CourseService
from app.services.file_service import FileService, FolderService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/courses/{course_id}", response_class=HTMLResponse)
async def view_course(
    request: Request,
    course_id: int,
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course_svc = CourseService(db)
    file_svc = FileService(db)
    folder_svc = FolderService(db)
    audit_repo = AuditLogRepository(db)

    course = course_svc.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    folders = folder_svc.get_by_course(course_id)
    folder_files = {f.id: folder_svc.files_in_folder(f.id) for f in folders}
    unfoldered = file_svc.get_unfoldered(course_id)
    search_results = file_svc.search(course_id, q) if q else None
    audit_logs = audit_repo.get_by_course(course_id, limit=30)
    can_upload = current_user.is_professor and current_user.department_id == course.department_id

    return templates.TemplateResponse("courses/view.html", {
        "request": request,
        "current_user": current_user,
        "course": course,
        "folders": folders,
        "folder_files": folder_files,
        "unfoldered": unfoldered,
        "search_results": search_results,
        "search_query": q,
        "audit_logs": audit_logs,
        "can_upload": can_upload,
    })


@router.get("/courses/create/new", response_class=HTMLResponse)
async def create_course_page(
    request: Request,
    current_user: User = Depends(require_professor),
):
    return templates.TemplateResponse("courses/create.html", {
        "request": request,
        "current_user": current_user,
        "error": None,
    })


@router.post("/courses/create/new", response_class=HTMLResponse)
async def create_course_submit(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    svc = CourseService(db)
    course, err = svc.create(name, code, description, current_user)
    if err:
        return templates.TemplateResponse("courses/create.html", {
            "request": request,
            "current_user": current_user,
            "error": err,
        }, status_code=400)
    return RedirectResponse(url=f"/courses/{course.id}", status_code=302)


@router.post("/courses/{course_id}/folders/create")
async def create_folder(
    request: Request,
    course_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    course_svc = CourseService(db)
    course = course_svc.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404)
    folder_svc = FolderService(db)
    folder, err = folder_svc.create(name, course, current_user)
    redirect = RedirectResponse(url=f"/courses/{course_id}", status_code=302)
    if err:
        # Pass error via flash-style query param — template reads it
        redirect = RedirectResponse(url=f"/courses/{course_id}?folder_error={err}", status_code=302)
    return redirect


@router.post("/courses/{course_id}/folders/{folder_id}/delete")
async def delete_folder(
    course_id: int,
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    folder_svc = FolderService(db)
    folder = folder_svc.get_by_id(folder_id)
    if not folder or folder.course_id != course_id:
        raise HTTPException(status_code=404)
    ok, err = folder_svc.delete(folder, current_user)
    if not ok:
        raise HTTPException(status_code=403, detail=err)
    return RedirectResponse(url=f"/courses/{course_id}", status_code=302)
