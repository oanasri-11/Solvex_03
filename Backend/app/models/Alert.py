"""Alert model."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"
    """
    Alert model.
    """
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="new", nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile", back_populates="alerts")

    alert_readings = relationship("AlertReading", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return f"<Alert(id={self.id}, patient_id={self.patient_id}, type={self.alert_type}, status={self.status})>"
