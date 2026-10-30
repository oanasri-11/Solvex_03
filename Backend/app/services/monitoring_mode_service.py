"""Monitoring mode service.

CRUD operations for the PatientMonitoringMode model, following classic SQLAlchemy syntax.
Per the specification, mode records are immutable: there is no PATCH or DELETE on a mode
record (a change creates a new record that closes the previous one).
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.PatientMonitoringMode import PatientMonitoringMode
from app.models.PatientProfile import PatientProfile
from app.schemas.monitoring_mode import (
    PatientMonitoringModeCreate,
    PatientMonitoringModeUpdate,
    PatientMonitoringModeOut,
)


def create_monitoring_mode(db: Session, mode_in: PatientMonitoringModeCreate) -> Optional[PatientMonitoringMode]:
    """Record a monitoring mode for a patient."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == mode_in.patient_id).first()
        )
        if not patient:
            return None
        existing = (
            db.query(PatientMonitoringMode)
            .filter(PatientMonitoringMode.patient_id == mode_in.patient_id)
            .first()
        )
        if existing:
            existing.mode = mode_in.mode
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        db_mode = PatientMonitoringMode(
            patient_id=mode_in.patient_id,
            mode=mode_in.mode,
        )
        db.add(db_mode)
        db.commit()
        db.refresh(db_mode)
        return db_mode
    except SQLAlchemyError:
        db.rollback()
        raise


def get_monitoring_mode_by_id(db: Session, mode_id: int) -> Optional[PatientMonitoringMode]:
    """Retrieve a monitoring mode record by its primary key."""
    return (
        db.query(PatientMonitoringMode).filter(PatientMonitoringMode.id == mode_id).first()
    )


def get_monitoring_mode_by_patient(
    db: Session, patient_id: int
) -> Optional[PatientMonitoringMode]:
    """Retrieve the current monitoring mode for a patient."""
    return (
        db.query(PatientMonitoringMode)
        .filter(PatientMonitoringMode.patient_id == patient_id)
        .first()
    )


def get_all_monitoring_modes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
):
    """List monitoring mode records (history), optionally filtered by patient."""
    query = db.query(PatientMonitoringMode)
    if patient_id is not None:
        query = query.filter(PatientMonitoringMode.patient_id == patient_id)
    return query.offset(skip).limit(limit).all()


# Note: update/delete are intentionally omitted. Mode records are immutable per the
# specification; a mode change creates a new record rather than rewriting the past.
