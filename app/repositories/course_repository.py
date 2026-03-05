from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.course import Course


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Course | None:
        return self.db.get(Course, course_id)

    def get_by_department(self, dept_id: int) -> list[Course]:
        return list(self.db.execute(
            select(Course).where(Course.department_id == dept_id).order_by(Course.name)
        ).scalars().all())

    def search_by_name(self, query: str) -> list[Course]:
        pattern = f"%{query}%"
        return list(self.db.execute(
            select(Course).where(Course.name.ilike(pattern)).order_by(Course.name)
        ).scalars().all())

    def save(self, course: Course) -> Course:
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.db.delete(course)
        self.db.commit()
