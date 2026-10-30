"""ScheduleSlot model."""

<<<<<<< HEAD
from sqlalchemy import DateTime, ForeignKey, Integer, String, func,Column
=======
from sqlalchemy import DateTime, ForeignKey, Integer, String, Column, JSON
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import relationship

from app.db.base import Base


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

<<<<<<< HEAD
    # Enum-like values stored as String: "pending", "completed", "missed"
=======
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    schedule_id = Column(
        Integer,
        ForeignKey("measurement_schedules.id"),
        nullable=False,
        index=True,
    )
<<<<<<< HEAD
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending | completed | missed
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    reading_id = Column(
        Integer,
        ForeignKey("blood_pressure_readings.id"),
        nullable=True,
<<<<<<< HEAD
        index=True,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    schedule = relationship("MeasurementSchedule", back_populates="slots")
    reading = relationship("BloodPressureReading", uselist=False)
=======
    )
    reason = Column(String(255), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    schedule = relationship("MeasurementSchedule", back_populates="slots")
    reading = relationship("BloodPressureReading", foreign_keys=[reading_id])
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489

    def __repr__(self):  # pragma: no cover
        return f"<ScheduleSlot(id={self.id}, schedule_id={self.schedule_id}, status={self.status})>"
