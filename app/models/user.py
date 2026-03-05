from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'professor' | 'student'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="users")
    uploaded_files: Mapped[list["File"]] = relationship("File", back_populates="uploader")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")

    @property
    def is_professor(self) -> bool:
        return self.role == "professor"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
