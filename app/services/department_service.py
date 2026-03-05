from sqlalchemy.orm import Session
from app.models.department import Department
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository


class DepartmentService:
    def __init__(self, db: Session):
        self.repo = DepartmentRepository(db)

    def get_all(self) -> list[Department]:
        return self.repo.get_all()

    def get_by_id(self, dept_id: int) -> Department | None:
        return self.repo.get_by_id(dept_id)

    def split_for_user(self, user: User) -> tuple[Department, list[Department]]:
        """Returns (my_department, [other_departments])."""
        all_depts = self.repo.get_all()
        my_dept = user.department
        others = [d for d in all_depts if d.id != my_dept.id]
        return my_dept, others
