from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.file import File


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, file_id: int) -> File | None:
        return self.db.get(File, file_id)

    def get_by_course(self, course_id: int) -> list[File]:
        return list(self.db.execute(
            select(File).where(File.course_id == course_id).order_by(File.upload_date.desc())
        ).scalars().all())

    def get_by_folder(self, folder_id: int) -> list[File]:
        return list(self.db.execute(
            select(File).where(File.folder_id == folder_id).order_by(File.upload_date.desc())
        ).scalars().all())

    def get_unfoldered_by_course(self, course_id: int) -> list[File]:
        return list(self.db.execute(
            select(File).where(File.course_id == course_id, File.folder_id.is_(None))
            .order_by(File.upload_date.desc())
        ).scalars().all())

    def search_in_course(self, course_id: int, query: str) -> list[File]:
        pattern = f"%{query}%"
        return list(self.db.execute(
            select(File)
            .where(File.course_id == course_id, File.original_name.ilike(pattern))
            .order_by(File.original_name)
        ).scalars().all())

    def save(self, file: File) -> File:
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    def delete(self, file: File) -> None:
        self.db.delete(file)
        self.db.commit()
