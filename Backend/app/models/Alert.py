<<<<<<< HEAD
"""Alert model."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func,Column
=======
"""Alert model with tiers, SLA escalation, and justification evidence."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, Column, JSON
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"
<<<<<<< HEAD
    """
    Alert model.
    """
=======

>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
<<<<<<< HEAD
    status = Column(String(50), default="new", nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile", back_populates="alerts")

    alert_readings = relationship("AlertReading", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return f"<Alert(id={self.id}, patient_id={self.patient_id}, type={self.alert_type}, status={self.status})>"
=======
    tier = Column(String(50), default="routine_out_of_range", nullable=True)  # routine_out_of_range, persistent_elevation, severe_single_reading, critical_emergency
    trigger_type = Column(String(50), default="single_reading", nullable=True)  # single_reading, trend_persistence, missed_data
    status = Column(String(50), default="new", nullable=False)
    lifecycle = Column(String(50), default="raised", nullable=True)  # raised, delivered, acknowledged, escalated, closed
    rule_version_id = Column(Integer, nullable=True)
    justification = Column(JSON, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    acknowledged_by = Column(Integer, nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    escalated_to_user_id = Column(Integer, nullable=True)
    closed_by = Column(Integer, nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    patient_acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile", back_populates="alerts")
    alert_readings = relationship("AlertReading", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return f"<Alert(id={self.id}, patient_id={self.patient_id}, type={self.alert_type}, tier={self.tier}, status={self.status})>"
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
