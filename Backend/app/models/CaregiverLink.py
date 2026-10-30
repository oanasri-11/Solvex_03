"""CaregiverLink model (Section 5b)."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Column, JSON, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class CaregiverLink(Base):
    __tablename__ = "caregiver_links"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    caregiver_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    invite_code = Column(String(64), unique=True, nullable=True, index=True)
    caregiver_name = Column(String(255), nullable=True)
    caregiver_contact = Column(String(255), nullable=True)
    scope = Column(JSON, nullable=False)  # ['record', 'confirm_slot', 'view_history', 'view_trend', 'reminders', 'help']
    notify_reminders = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="invited", nullable=False)  # invited, active, revoked
    consent_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile")
    caregiver_user = relationship("User", foreign_keys=[caregiver_user_id])

    def __repr__(self):  # pragma: no cover
        return f"<CaregiverLink(id={self.id}, patient_id={self.patient_id}, status={self.status})>"
