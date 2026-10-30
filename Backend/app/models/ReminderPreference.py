"""ReminderPreference model (Section 10)."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Column, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class ReminderPreference(Base):
    __tablename__ = "reminder_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    enabled = Column(Boolean, default=True, nullable=False)
    channel = Column(String(50), default="push", nullable=False)  # push, sms
    lead_minutes = Column(Integer, default=15, nullable=False)
    morning_time = Column(String(10), default="08:00", nullable=True)
    evening_time = Column(String(10), default="20:00", nullable=True)
    routine_day = Column(String(20), default="sunday", nullable=True)
    routine_time = Column(String(10), default="09:00", nullable=True)
    adaptive_missed_reminder = Column(Boolean, default=True, nullable=False)
    push_tokens = Column(JSON, default=list, nullable=True)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<ReminderPreference(patient_id={self.patient_id}, channel={self.channel})>"
