"""Reading service.

CRUD operations for the BloodPressureReading model, following classic SQLAlchemy syntax.
Readings are immutable: there is no PATCH, PUT or DELETE. A correction creates a new
reading that references the original (recheck_of_reading_id).
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.BloodPressureReading import BloodPressureReading
from app.models.patientprofile import PatientProfile
from app.schemas.measurement import (
    BloodPressureReadingCreate,
    BloodPressureReadingUpdate,
    BloodPressureReadingOut,
)


def create_blood_pressure_reading(
    db: Session, reading_in: BloodPressureReadingCreate
) -> BloodPressureReading:
    """Save a new blood pressure reading. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == reading_in.patient_id).first()
        )
        if not patient:
            return None
        db_reading = BloodPressureReading(
            patient_id=reading_in.patient_id,
            systolic=reading_in.systolic,
            diastolic=reading_in.diastolic,
            measured_at=reading_in.measured_at,
            recheck_of_reading_id=reading_in.recheck_of_reading_id,
            notes=reading_in.notes,
        )
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        return db_reading
    except SQLAlchemyError:
        db.rollback()
        raise


def get_blood_pressure_reading_by_id(
    db: Session, reading_id: int
) -> Optional[BloodPressureReading]:
    """Retrieve a reading by its primary key."""
    return (
        db.query(BloodPressureReading).filter(BloodPressureReading.id == reading_id).first()
    )


def get_all_blood_pressure_readings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
):
    """List readings, newest first, optionally filtered by patient."""
    query = db.query(BloodPressureReading)
    if patient_id is not None:
        query = query.filter(BloodPressureReading.patient_id == patient_id)
    return query.order_by(BloodPressureReading.created_at.desc()).offset(skip).limit(limit).all()


# Note: update/delete are intentionally omitted. Readings are immutable per the
# specification. A correction is a new POST with recheck_of_reading_id set; the
# original record stays intact.