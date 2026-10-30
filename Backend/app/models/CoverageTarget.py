"""CoverageTarget model (Section 4b)."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Column, JSON, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class CoverageTarget(Base):
    __tablename__ = "coverage_targets"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    backup_doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    after_hours_owner_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=True)
    coverage_hours = Column(JSON, nullable=True)  # working hours specification
    version = Column(Integer, default=1, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    doctor = relationship("DoctorProfile", foreign_keys=[doctor_id])
    backup_doctor = relationship("DoctorProfile", foreign_keys=[backup_doctor_id])

    def __repr__(self):  # pragma: no cover
        return f"<CoverageTarget(doctor_id={self.doctor_id}, backup={self.backup_doctor_id})>"
