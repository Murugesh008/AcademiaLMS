from sqlalchemy.orm import Session
from app.models.course import Course
from app.models.user import User
from app.repositories.course_repository import CourseRepository
from app.repositories.department_repository import DepartmentRepository


class CourseService:
    def __init__(self, db: Session):
        self.repo = CourseRepository(db)
        self.dept_repo = DepartmentRepository(db)

    def get_by_id(self, course_id: int) -> Course | None:
        return self.repo.get_by_id(course_id)

    def get_by_department(self, dept_id: int) -> list[Course]:
        return self.repo.get_by_department(dept_id)

    def search(self, query: str) -> list[Course]:
        if not query or not query.strip():
            return []
        return self.repo.search_by_name(query.strip())

    def create(self, name: str, code: str, description: str, professor: User) -> tuple[Course | None, str]:
        dept = self.dept_repo.get_by_id(professor.department_id)
        if not dept:
            return None, "Department not found."
        course = Course(
            name=name.strip(),
            code=code.strip().upper(),
            description=description.strip() if description else None,
            department_id=dept.id,
        )
        self.repo.save(course)
        return course, ""

    def professor_can_modify(self, user: User, course: Course) -> bool:
        return user.is_professor and user.department_id == course.department_id
