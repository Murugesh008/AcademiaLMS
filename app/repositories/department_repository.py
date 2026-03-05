from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.department import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, dept_id: int) -> Department | None:
        return self.db.get(Department, dept_id)

    def get_by_code(self, code: str) -> Department | None:
        return self.db.execute(
            select(Department).where(Department.code == code)
        ).scalar_one_or_none()

    def get_all(self) -> list[Department]:
        return list(self.db.execute(
            select(Department).order_by(Department.name)
        ).scalars().all())

    def save(self, dept: Department) -> Department:
        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)
        return dept
