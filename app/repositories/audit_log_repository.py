from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_course(self, course_id: int, limit: int = 50) -> list[AuditLog]:
        return list(self.db.execute(
            select(AuditLog)
            .where(AuditLog.course_id == course_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        ).scalars().all())

    def save(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
