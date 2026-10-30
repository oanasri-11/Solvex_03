"""OfficeReading service (Section 7c)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.OfficeReading import OfficeReading
from app.models.patientprofile import PatientProfile


def record_office_reading(
    db: Session,
    patient_id: int,
    systolic: Optional[int] = None,
    diastolic: Optional[int] = None,
    pulse: Optional[int] = None,
    measured_at: Optional[datetime] = None,
    recorded_by: Optional[int] = None,
    note: Optional[str] = None,
    reading_in: Optional[Any] = None,
    doctor_user_id: Optional[int] = None,
) -> OfficeReading:
    if reading_in is not None:
        systolic = systolic if systolic is not None else getattr(reading_in, "systolic", None)
        diastolic = diastolic if diastolic is not None else getattr(reading_in, "diastolic", None)
        pulse = pulse if pulse is not None else getattr(reading_in, "pulse", None)
        measured_at = measured_at or getattr(reading_in, "measured_at", None)
        note = note or getattr(reading_in, "note", None)
    recorded_by = recorded_by or doctor_user_id or 1
    measured_at = measured_at or datetime.now(timezone.utc)
    systolic = systolic if systolic is not None else 120
    diastolic = diastolic if diastolic is not None else 80
    """Record office BP measurement. Never analysed by alert rules (used for white-coat comparison)."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    reading = OfficeReading(
        patient_id=patient_id,
        systolic=systolic,
        diastolic=diastolic,
        pulse=pulse,
        measured_at=measured_at,
        recorded_by=recorded_by,
        note=note,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def get_office_readings(db: Session, patient_id: int) -> List[OfficeReading]:
    """Retrieve office reading history."""
    return db.query(OfficeReading).filter(
        OfficeReading.patient_id == patient_id
    ).order_by(OfficeReading.measured_at.desc()).all()
