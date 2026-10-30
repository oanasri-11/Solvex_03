"""PatientCondition model."""

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class PatientCondition(Base):
    __tablename__ = "patient_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    condition_name = Column(String(255), nullable=False)
    diagnosed_at = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile", back_populates="conditions")

    def __repr__(self):  # pragma: no cover
        return f"<PatientCondition(id={self.id}, patient_id={self.patient_id}, condition_name={self.condition_name})>"
