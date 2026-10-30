"""BloodPressureReading model with self-referencing recheck relationship."""

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base

"""
    BloodPressureReading model.
    """

class BloodPressureReading(Base):
    __tablename__ = "blood_pressure_readings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.id"),
        nullable=False,
        index=True,
    )
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    # Self-referencing foreign key: a reading can be a recheck of another reading
    recheck_of_reading_id = Column(
        Integer,
        ForeignKey("blood_pressure_readings.id"),
        nullable=True,
        index=True,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile", back_populates="readings")

    # Self-referencing relationships
    recheck_of = relationship(
        "BloodPressureReading",
        remote_side=[id],
        uselist=False,
        back_populates="rechecks",
    )
    rechecks = relationship(
        "BloodPressureReading",
        back_populates="recheck_of",
    )

    # Link to alerts that reference this reading
    alert_readings = relationship("AlertReading", back_populates="reading")

    def __repr__(self):  # pragma: no cover
        return f"<BloodPressureReading(id={self.id}, patient_id={self.patient_id}, {self.systolic}/{self.diastolic})>"
