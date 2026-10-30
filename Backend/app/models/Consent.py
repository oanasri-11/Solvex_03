"""Consent model (SC5)."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    type = Column(String(50), nullable=False)  # data_sharing, monitoring_mode, caregiver_access
    text_version = Column(String(50), nullable=False)
    accepted = Column(Boolean, default=True, nullable=False)
    accepted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    recorded_by = Column(Integer, nullable=True)
    method = Column(String(50), default="in_app", nullable=False)  # in_app, paper, verbal
    witness_note = Column(Text, nullable=True)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<Consent(id={self.id}, patient_id={self.patient_id}, type={self.type}, accepted={self.accepted})>"
