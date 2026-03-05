from app.repositories.user_repository import UserRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.folder_repository import FolderRepository
from app.repositories.file_repository import FileRepository
from app.repositories.audit_log_repository import AuditLogRepository

__all__ = [
    "UserRepository", "DepartmentRepository", "CourseRepository",
    "FolderRepository", "FileRepository", "AuditLogRepository",
]
