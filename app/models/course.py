from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("code", "department_id", name="uq_course_code_dept"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="courses")
    folders: Mapped[list["Folder"]] = relationship("Folder", back_populates="course", cascade="all, delete-orphan")
    files: Mapped[list["File"]] = relationship("File", back_populates="course", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course {self.code}>"
