"""FollowUpAction model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class FollowUpAction(Base):
    __tablename__ = "follow_up_actions"

    # Enum-like values stored as String:
    #   type: "call", "visit", "medication_adjustment", "lifestyle"
    #   status: "pending", "completed", "overdue"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    type = Column(String(50), nullable=False)  # call | visit | medication_adjustment | lifestyle
    status = Column(String(50), default="pending", nullable=False)  # pending | completed | overdue
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    patient = relationship("PatientProfile", back_populates="follow_up_actions")

    def __repr__(self):  # pragma: no cover
        return f"<FollowUpAction(id={self.id}, patient_id={self.patient_id}, type={self.type}, status={self.status})>"
