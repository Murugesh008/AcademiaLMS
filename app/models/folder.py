from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (UniqueConstraint("name", "course_id", name="uq_folder_name_course"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="folders")
    files: Mapped[list["File"]] = relationship("File", back_populates="folder")

    def __repr__(self) -> str:
        return f"<Folder {self.name}>"
