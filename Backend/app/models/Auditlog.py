"""AuditLog model (table: audit_logs)."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, func,Column
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "auditlog"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    action = Column(String(255), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):  # pragma: no cover
        return f"<AuditLog(id={self.id}, action={self.action}, table_name={self.table_name})>"
