from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.department_service import DepartmentService
from app.services.course_service import CourseService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dept_svc = DepartmentService(db)
    course_svc = CourseService(db)

    my_dept, other_depts = dept_svc.split_for_user(current_user)
    my_courses = course_svc.get_by_department(my_dept.id)

    other_dept_courses = [
        (dept, course_svc.get_by_department(dept.id))
        for dept in other_depts
    ]

    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "current_user": current_user,
        "my_dept": my_dept,
        "my_courses": my_courses,
        "other_dept_courses": other_dept_courses,
    })
