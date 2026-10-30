"""PriorityAssessment model with clinical & behavioral triage factors."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Column, JSON, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class PriorityAssessment(Base):
    __tablename__ = "priority_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    assessor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    level = Column(String(50), default="medium", nullable=False)  # low | medium | high | urgent
    priority_level = Column(String(50), default="P4_routine", nullable=True)  # P1_critical, P2_high, P3_moderate, P4_routine, not_triaged
    score = Column(Float, default=0.0, nullable=True)
    reasons = Column(JSON, nullable=True)  # coded array of reasons
    inputs = Column(JSON, nullable=True)  # bp_level, trend_persistence, adherence_rate, age_band, conditions, etc.
    rule_version_id = Column(Integer, nullable=True)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)

    patient = relationship("PatientProfile", back_populates="priority_assessments")

    def __repr__(self):  # pragma: no cover
        return f"<PriorityAssessment(id={self.id}, patient_id={self.patient_id}, level={self.priority_level})>"
