"""ContactRequest model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class ContactRequest(Base):
    __tablename__ = "contact_requests"

    # Enum-like values stored as String: "open", "responded", "closed"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id"),
        nullable=True,
        index=True,
    )
    message = Column(Text, nullable=False)
    status = Column(String(50), default="open", nullable=False)  # open | responded | closed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("PatientProfile", back_populates="contact_requests")
    doctor = relationship("DoctorProfile")

    def __repr__(self):  # pragma: no cover
        return f"<ContactRequest(id={self.id}, patient_id={self.patient_id}, status={self.status})>"
