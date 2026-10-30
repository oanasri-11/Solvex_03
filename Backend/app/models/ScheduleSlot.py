"""ScheduleSlot model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    # Enum-like values stored as String: "pending", "completed", "missed"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    schedule_id = Column(
        Integer,
        ForeignKey("measurement_schedules.id"),
        nullable=False,
        index=True,
    )
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending | completed | missed
    reading_id = Column(
        Integer,
        ForeignKey("blood_pressure_readings.id"),
        nullable=True,
        index=True,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    schedule = relationship("MeasurementSchedule", back_populates="slots")
    reading = relationship("BloodPressureReading", uselist=False)

    def __repr__(self):  # pragma: no cover
        return f"<ScheduleSlot(id={self.id}, schedule_id={self.schedule_id}, status={self.status})>"
