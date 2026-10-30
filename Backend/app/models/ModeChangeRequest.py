"""ModeChangeRequest model (Section 5)."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class ModeChangeRequest(Base):
    __tablename__ = "mode_change_requests"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    requested_mode = Column(String(50), nullable=False)  # self_monitoring, telemonitoring
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, declined
    resolved_by = Column(Integer, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<ModeChangeRequest(id={self.id}, patient_id={self.patient_id}, mode={self.requested_mode}, status={self.status})>"
