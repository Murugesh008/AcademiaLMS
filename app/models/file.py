from sqlalchemy import Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    folder_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("folders.id"), nullable=True)
    uploader_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="files")
    folder: Mapped["Folder | None"] = relationship("Folder", back_populates="files")
    uploader: Mapped["User"] = relationship("User", back_populates="uploaded_files")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="file")

    @property
    def size_human(self) -> str:
        size = float(self.file_size)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def __repr__(self) -> str:
        return f"<File {self.original_name}>"
