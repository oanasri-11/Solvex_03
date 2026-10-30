"""PriorityAssessment model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class PriorityAssessment(Base):
    __tablename__ = "priority_assessments"

    # Enum-like values stored as String: "low", "medium", "high", "urgent"
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
        index=True,
    )
    level = Column(String(50), nullable=False)  # low | medium | high | urgent
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)

    patient = relationship("PatientProfile", back_populates="priority_assessments")
    assessor = relationship("User", back_populates="priority_assessments")

    def __repr__(self):  # pragma: no cover
        return f"<PriorityAssessment(id={self.id}, patient_id={self.patient_id}, level={self.level})>"
