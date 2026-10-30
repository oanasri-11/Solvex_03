"""OfficeReading model (Section 7c)."""

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class OfficeReading(Base):
    __tablename__ = "office_readings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=True)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    recorded_by = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<OfficeReading(id={self.id}, patient_id={self.patient_id}, {self.systolic}/{self.diastolic})>"
