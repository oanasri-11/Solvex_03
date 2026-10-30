"""CaseReview model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class CaseReview(Base):
    __tablename__ = "case_reviews"

    # Enum-like values stored as String: "draft", "completed"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    reviewer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    status = Column(String(50), default="draft", nullable=False)  # draft | completed
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    patient = relationship("PatientProfile", back_populates="case_reviews")
    reviewer = relationship("User", back_populates="case_reviews")

    def __repr__(self):  # pragma: no cover
        return f"<CaseReview(id={self.id}, patient_id={self.patient_id}, status={self.status})>"
