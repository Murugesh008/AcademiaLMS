import os
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, Request

from config import settings
from app.models.file import File
from app.models.folder import Folder
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.course import Course
from app.repositories.file_repository import FileRepository
from app.repositories.folder_repository import FolderRepository
from app.repositories.audit_log_repository import AuditLogRepository


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in settings.ALLOWED_EXTENSIONS


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower() if "." in filename else "bin"


class FileService:
    def __init__(self, db: Session):
        self.file_repo = FileRepository(db)
        self.folder_repo = FolderRepository(db)
        self.audit_repo = AuditLogRepository(db)
        self.db = db

    async def upload(
        self,
        upload: UploadFile,
        course: Course,
        uploader: User,
        folder_id: int | None,
        request: Request,
    ) -> tuple[File | None, str]:
        if not upload or not upload.filename:
            return None, "No file selected."
        if not _allowed(upload.filename):
            return None, f"File type not allowed. Allowed: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"

        # Validate folder
        folder: Folder | None = None
        if folder_id:
            folder = self.folder_repo.get_by_id(folder_id)
            if not folder or folder.course_id != course.id:
                return None, "Invalid folder."

        # Read content and enforce size limit
        content = await upload.read()
        if len(content) > settings.MAX_UPLOAD_BYTES:
            return None, "File exceeds 50 MB limit."

        # Safe stored path: uploads/<DEPT>/<COURSE>/<uuid>.<ext>
        dept_code = course.department.code
        course_code = course.code
        dest_dir = settings.UPLOAD_DIR / dept_code / course_code
        dest_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}.{_ext(upload.filename)}"
        dest_path = dest_dir / stored_filename
        dest_path.write_bytes(content)

        # Relative stored_name so UPLOAD_DIR can move
        stored_name = f"{dept_code}/{course_code}/{stored_filename}"

        record = File(
            original_name=upload.filename,
            stored_name=stored_name,
            file_size=len(content),
            mime_type=upload.content_type,
            course_id=course.id,
            folder_id=folder.id if folder else None,
            uploader_id=uploader.id,
        )
        self.file_repo.save(record)

        self.audit_repo.save(AuditLog(
            user_id=uploader.id,
            action="upload",
            file_id=record.id,
            file_name=upload.filename,
            course_id=course.id,
            ip_address=request.client.host if request.client else None,
            details=f"Folder: {folder.name}" if folder else "Root",
        ))
        return record, ""

    def delete(self, file: File, user: User, request: Request) -> tuple[bool, str]:
        if user.is_student:
            return False, "Students cannot delete files."
        if user.department_id != file.course.department_id:
            return False, "You can only delete files in your own department."

        path = settings.UPLOAD_DIR / file.stored_name
        if path.exists():
            path.unlink()

        self.audit_repo.save(AuditLog(
            user_id=user.id,
            action="delete",
            file_id=None,
            file_name=file.original_name,
            course_id=file.course_id,
            ip_address=request.client.host if request.client else None,
            details=f"Deleted by {user.full_name}",
        ))
        self.file_repo.delete(file)
        return True, ""

    def get_by_id(self, file_id: int) -> File | None:
        return self.file_repo.get_by_id(file_id)

    def get_unfoldered(self, course_id: int) -> list[File]:
        return self.file_repo.get_unfoldered_by_course(course_id)

    def search(self, course_id: int, query: str) -> list[File]:
        if not query:
            return self.file_repo.get_by_course(course_id)
        return self.file_repo.search_in_course(course_id, query.strip())

    def disk_path(self, file: File) -> Path:
        return settings.UPLOAD_DIR / file.stored_name


class FolderService:
    def __init__(self, db: Session):
        self.repo = FolderRepository(db)
        self.db = db

    def get_by_id(self, folder_id: int) -> Folder | None:
        return self.repo.get_by_id(folder_id)

    def get_by_course(self, course_id: int) -> list[Folder]:
        return self.repo.get_by_course(course_id)

    def files_in_folder(self, folder_id: int) -> list[File]:
        from app.repositories.file_repository import FileRepository
        return FileRepository(self.db).get_by_folder(folder_id)

    def create(self, name: str, course: Course, user: User) -> tuple[Folder | None, str]:
        if not user.is_professor:
            return None, "Only professors can create folders."
        if user.department_id != course.department_id:
            return None, "You can only create folders in your own department."
        existing = self.repo.get_by_name_and_course(name.strip(), course.id)
        if existing:
            return None, "A folder with that name already exists."
        folder = Folder(name=name.strip(), course_id=course.id)
        self.repo.save(folder)
        return folder, ""

    def delete(self, folder: Folder, user: User) -> tuple[bool, str]:
        if not user.is_professor:
            return False, "Only professors can delete folders."
        if user.department_id != folder.course.department_id:
            return False, "You can only delete folders in your own department."
        # Detach files to root before deleting folder
        for f in folder.files:
            f.folder_id = None
        self.db.commit()
        self.repo.delete(folder)
        return True, ""
