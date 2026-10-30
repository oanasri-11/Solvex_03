"""PatientMonitoringMode model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class PatientMonitoringMode(Base):
    __tablename__ = "patient_monitoring_modes"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        unique=False,
        nullable=False,
        index=True,
    )
    mode = Column(String(50), default="self_monitoring", nullable=False)  # self_monitoring | telemonitoring
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    changed_by = Column(Integer, nullable=True)
    consent_id = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    patient = relationship("PatientProfile", back_populates="monitoring_mode")

    def __repr__(self):  # pragma: no cover
        return f"<PatientMonitoringMode(id={self.id}, patient_id={self.patient_id}, mode={self.mode})>"
