"""DoctorPatientAssignment model (many-to-many link between doctors and patients)."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class DoctorPatientAssignment(Base):
    __tablename__ = "doctor_patient_assignments"
    __table_args__ = (
        UniqueConstraint("doctor_id", "patient_id", name="uq_doctor_patient_assignment"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id"),
        nullable=False,
        index=True,
    )
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    doctor = relationship("DoctorProfile", back_populates="assignments")
    patient = relationship("PatientProfile", back_populates="assignments")

    def __repr__(self):  # pragma: no cover
        return f"<DoctorPatientAssignment(id={self.id}, doctor_id={self.doctor_id}, patient_id={self.patient_id})>"
