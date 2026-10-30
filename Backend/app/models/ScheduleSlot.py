"""ScheduleSlot model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Column, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    schedule_id = Column(
        Integer,
        ForeignKey("measurement_schedules.id"),
        nullable=False,
        index=True,
    )
    cycle_id = Column(String(64), nullable=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=True, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=True)
    window_start = Column(DateTime(timezone=True), nullable=True)
    window_end = Column(DateTime(timezone=True), nullable=True)
    readings_required = Column(Integer, default=2, nullable=True)
    readings_received = Column(Integer, default=0, nullable=True)
    reading_ids = Column(JSON, nullable=True)
    status = Column(String(50), default="upcoming", nullable=False)  # upcoming, taken, partial, not_taken, missed, completed, pending
    reading_id = Column(
        Integer,
        ForeignKey("blood_pressure_readings.id"),
        nullable=True,
    )
    reason = Column(String(255), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    schedule = relationship("MeasurementSchedule", back_populates="slots")
    reading = relationship("BloodPressureReading", foreign_keys=[reading_id])

    def __repr__(self):  # pragma: no cover
        return f"<ScheduleSlot(id={self.id}, schedule_id={self.schedule_id}, status={self.status})>"
