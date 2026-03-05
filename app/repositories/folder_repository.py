from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.folder import Folder


class FolderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, folder_id: int) -> Folder | None:
        return self.db.get(Folder, folder_id)

    def get_by_course(self, course_id: int) -> list[Folder]:
        return list(self.db.execute(
            select(Folder).where(Folder.course_id == course_id).order_by(Folder.name)
        ).scalars().all())

    def get_by_name_and_course(self, name: str, course_id: int) -> Folder | None:
        return self.db.execute(
            select(Folder).where(Folder.name == name, Folder.course_id == course_id)
        ).scalar_one_or_none()

    def save(self, folder: Folder) -> Folder:
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def delete(self, folder: Folder) -> None:
        self.db.delete(folder)
        self.db.commit()
