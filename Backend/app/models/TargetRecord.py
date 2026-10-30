"""TargetRecord model (Section 2, SC4)."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class TargetRecord(Base):
    __tablename__ = "target_records"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    basis = Column(String(50), default="home_average", nullable=False)
    reason_code = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    set_by = Column(Integer, nullable=False)
    set_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile")

    def __repr__(self):  # pragma: no cover
        return f"<TargetRecord(id={self.id}, patient_id={self.patient_id}, target={self.systolic}/{self.diastolic})>"
