from fastapi import APIRouter, Request, Depends, UploadFile, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, require_professor
from app.models.user import User
from app.services.course_service import CourseService
from app.services.file_service import FileService

router = APIRouter()


@router.post("/files/upload/{course_id}")
async def upload_file(
    request: Request,
    course_id: int,
    file: UploadFile,
    folder_id: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    course_svc = CourseService(db)
    course = course_svc.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404)
    if current_user.department_id != course.department_id:
        raise HTTPException(status_code=403, detail="You can only upload to your department's courses.")

    fid = int(folder_id) if folder_id.strip().isdigit() else None
    file_svc = FileService(db)
    record, err = await file_svc.upload(file, course, current_user, fid, request)

    if err:
        return RedirectResponse(url=f"/courses/{course_id}?upload_error={err}", status_code=302)
    return RedirectResponse(url=f"/courses/{course_id}", status_code=302)


@router.get("/files/download/{file_id}")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # any logged-in user
):
    file_svc = FileService(db)
    record = file_svc.get_by_id(file_id)
    if not record:
        raise HTTPException(status_code=404)

    disk_path = file_svc.disk_path(record)
    if not disk_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(
        path=str(disk_path),
        filename=record.original_name,
        media_type="application/octet-stream",
    )


@router.post("/files/delete/{file_id}")
async def delete_file(
    request: Request,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    file_svc = FileService(db)
    record = file_svc.get_by_id(file_id)
    if not record:
        raise HTTPException(status_code=404)

    course_id = record.course_id
    ok, err = file_svc.delete(record, current_user, request)
    if not ok:
        raise HTTPException(status_code=403, detail=err)
    return RedirectResponse(url=f"/courses/{course_id}", status_code=302)
