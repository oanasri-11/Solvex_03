"""MeasurementSchedule model."""

<<<<<<< HEAD
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func,Column
from sqlalchemy.dialects.postgresql import JSON
=======
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func, Column, JSON
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import relationship

from app.db.base import Base


class MeasurementSchedule(Base):
    __tablename__ = "measurement_schedules"

<<<<<<< HEAD
    # Enum-like values stored as String: "daily", "weekly", "biweekly", "monthly"
=======
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
<<<<<<< HEAD
    frequency = Column(String(50), nullable=False)  # daily | weekly | biweekly | monthly
    time_of_day = Column(String(10), nullable=True)  # e.g. "08:00"
    # Days of week stored as JSON array, e.g. [1, 3, 5]
    days_of_week = Column(JSON, nullable=True)
=======
    frequency = Column(String(50), default="daily", nullable=False)  # daily | weekly | biweekly | monthly
    time_of_day = Column(String(10), nullable=True)  # e.g. "08:00"
    days_of_week = Column(JSON, nullable=True)

    # v3 fields
    owner = Column(String(50), default="doctor", nullable=True)  # patient | doctor
    protocol = Column(String(50), default="722_followup", nullable=True)  # 722_diagnostic, 722_followup, maintenance, custom
    readings_per_slot = Column(Integer, default=2, nullable=True)
    min_gap_seconds = Column(Integer, default=60, nullable=True)
    windows = Column(JSON, nullable=True)  # morning & evening windows
    cycle_length_days = Column(Integer, default=7, nullable=True)
    pattern = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    version = Column(Integer, default=1, nullable=True)
    pending_approval = Column(Boolean, default=False, nullable=True)
    created_by = Column(Integer, nullable=True)
    approved_by = Column(Integer, nullable=True)

>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    patient = relationship("PatientProfile", back_populates="schedules")
<<<<<<< HEAD

    slots = relationship("ScheduleSlot", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return f"<MeasurementSchedule(id={self.id}, patient_id={self.patient_id}, frequency={self.frequency})>"
=======
    slots = relationship("ScheduleSlot", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return f"<MeasurementSchedule(id={self.id}, patient_id={self.patient_id}, protocol={self.protocol}, active={self.is_active})>"
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
