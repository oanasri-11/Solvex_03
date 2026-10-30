"""TreatmentEvent model (Section 7b)."""

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class TreatmentEvent(Base):
    __tablename__ = "treatment_events"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(50), nullable=False)  # started, dose_changed, stopped
    drug_class = Column(String(100), nullable=False)  # ACEi, ARB, CCB, Thiazide, BB, etc.
    drug_name = Column(String(255), nullable=False)
    dose = Column(String(100), nullable=False)
    effective_date = Column(Date, nullable=False)
    recorded_by = Column(Integer, nullable=False)
    corrects_event_id = Column(Integer, ForeignKey("treatment_events.id"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<TreatmentEvent(id={self.id}, patient_id={self.patient_id}, drug={self.drug_name}, type={self.event_type})>"
