"""PatientHelpRequest model."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class PatientHelpRequest(Base):
    __tablename__ = "patient_help_requests"

    # Enum-like values stored as String:
    #   type: "medication", "device", "general"
    #   status: "open", "in_progress", "resolved", "closed"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    type = Column(String(50), nullable=False)  # medication | device | general
    status = Column(String(50), default="open", nullable=False)  # open | in_progress | resolved | closed
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile", back_populates="help_requests")

    def __repr__(self):  # pragma: no cover
        return f"<PatientHelpRequest(id={self.id}, patient_id={self.patient_id}, type={self.type}, status={self.status})>"
