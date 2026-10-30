"""MeasurementSchedule model."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func,Column
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class MeasurementSchedule(Base):
    __tablename__ = "measurement_schedules"

    # Enum-like values stored as String: "daily", "weekly", "biweekly", "monthly"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    frequency = Column(String(50), nullable=False)  # daily | weekly | biweekly | monthly
    time_of_day = Column(String(10), nullable=True)  # e.g. "08:00"
    # Days of week stored as JSON array, e.g. [1, 3, 5]
    days_of_week = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    patient = relationship("PatientProfile", back_populates="schedules")

    slots = relationship("ScheduleSlot", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return f"<MeasurementSchedule(id={self.id}, patient_id={self.patient_id}, frequency={self.frequency})>"
