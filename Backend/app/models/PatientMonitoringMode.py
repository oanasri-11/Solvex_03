"""PatientMonitoringMode model."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class PatientMonitoringMode(Base):
    __tablename__ = "patient_monitoring_modes"

    # Enum-like values stored as String: "continuous", "daily", "weekly", "off"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    mode = Column(String(50), nullable=False)  # continuous | daily | weekly | off
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    patient = relationship("PatientProfile", uselist=False, back_populates="monitoring_mode")

    def __repr__(self):  # pragma: no cover
        return f"<PatientMonitoringMode(id={self.id}, patient_id={self.patient_id}, mode={self.mode})>"
