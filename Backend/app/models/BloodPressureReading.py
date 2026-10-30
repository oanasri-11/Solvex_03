"""BloodPressureReading model with session grouping, verification, and audit flags."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Column, JSON, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class BloodPressureReading(Base):
    __tablename__ = "blood_pressure_readings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    session_id = Column(String(64), nullable=True, index=True)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=True)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    capture_method = Column(String(50), default="manual", nullable=True)  # manual, assisted, low_bandwidth_sms, connected_device
    entered_by = Column(String(50), default="patient", nullable=True)  # patient, caregiver, professional, device
    actor_id = Column(Integer, nullable=True)
    slot_id = Column(Integer, ForeignKey("schedule_slots.id"), nullable=True)
    mode_at_time = Column(String(50), nullable=True)
    verification_status = Column(String(50), default="accepted", nullable=True)  # accepted, needs_confirmation, confirmed_by_entrant
    status_level = Column(String(50), nullable=True)  # normal, elevated, stage_1, stage_2, severe
    replaces_reading_id = Column(Integer, ForeignKey("blood_pressure_readings.id"), nullable=True, index=True)
    recheck_of_reading_id = Column(
        Integer,
        ForeignKey("blood_pressure_readings.id"),
        nullable=True,
        index=True,
    )
    symptoms_reported = Column(JSON, nullable=True)
    medication_taken_today = Column(Boolean, nullable=True)
    data_quality_flags = Column(JSON, nullable=True)  # doctor-only: digit_preference, duplicate, late_entry
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile", back_populates="readings")

    # Self-referencing relationships
    recheck_of = relationship(
        "BloodPressureReading",
        remote_side=[id],
        foreign_keys=[recheck_of_reading_id],
        uselist=False,
        back_populates="rechecks",
    )
    rechecks = relationship(
        "BloodPressureReading",
        foreign_keys=[recheck_of_reading_id],
        back_populates="recheck_of",
    )

    # Link to alerts that reference this reading
    alert_readings = relationship("AlertReading", back_populates="reading")

    def __repr__(self):  # pragma: no cover
        return f"<BloodPressureReading(id={self.id}, patient_id={self.patient_id}, {self.systolic}/{self.diastolic})>"
