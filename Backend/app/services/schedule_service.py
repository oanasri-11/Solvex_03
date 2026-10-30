"""Schedule service.

CRUD operations for the MeasurementSchedule model, following classic SQLAlchemy syntax.
Only one schedule is active per patient. Deactivation is soft (is_active = False);
there is no hard delete.
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.MeasurementSchedule import MeasurementSchedule
from app.models.PatientProfile import PatientProfile
from app.schemas.schedule import (
    MeasurementScheduleCreate,
    MeasurementScheduleUpdate,
    MeasurementScheduleOut,
)


def create_measurement_schedule(
    db: Session, schedule_in: MeasurementScheduleCreate
) -> Optional[MeasurementSchedule]:
    """Define a measurement schedule for a patient. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == schedule_in.patient_id).first()
        )
        if not patient:
            return None
        is_active = getattr(schedule_in, "is_active", True)
        if is_active is None:
            is_active = True
        db_schedule = MeasurementSchedule(
            patient_id=schedule_in.patient_id,
            frequency=schedule_in.frequency,
            time_of_day=getattr(schedule_in, "time_of_day", None),
            days_of_week=getattr(schedule_in, "days_of_week", None),
            is_active=is_active,
        )
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except SQLAlchemyError:
        db.rollback()
        raise


def get_measurement_schedule_by_id(db: Session, schedule_id: int) -> Optional[MeasurementSchedule]:
    """Retrieve a schedule by its primary key."""
    return (
        db.query(MeasurementSchedule).filter(MeasurementSchedule.id == schedule_id).first()
    )


def get_all_measurement_schedules(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    """List schedules with optional patient_id / is_active filters."""
    query = db.query(MeasurementSchedule)
    if patient_id is not None:
        query = query.filter(MeasurementSchedule.patient_id == patient_id)
    if is_active is not None:
        query = query.filter(MeasurementSchedule.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def get_active_schedule_for_patient(
    db: Session, patient_id: int
) -> Optional[MeasurementSchedule]:
    """Retrieve the active schedule for a patient (only one is expected to be active)."""
    return (
        db.query(MeasurementSchedule)
        .filter(MeasurementSchedule.patient_id == patient_id, MeasurementSchedule.is_active == True)  # noqa: E712
        .first()
    )


def update_measurement_schedule(
    db: Session, schedule_id: int, schedule_in: MeasurementScheduleUpdate
) -> Optional[MeasurementSchedule]:
    """Edit a schedule. Per spec, an edit creates a new version; this implementation
    updates the existing record because the model carries no version field."""
    try:
        db_schedule = get_measurement_schedule_by_id(db, schedule_id)
        if not db_schedule:
            return None
        update_data = schedule_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_schedule, field, value)
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except SQLAlchemyError:
        db.rollback()
        raise


def deactivate_measurement_schedule(db: Session, schedule_id: int) -> Optional[MeasurementSchedule]:
    """Deactivate a schedule (is_active = False). No hard delete."""
    try:
        db_schedule = get_measurement_schedule_by_id(db, schedule_id)
        if not db_schedule:
            return None
        db_schedule.is_active = False
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except SQLAlchemyError:
        db.rollback()
        raise
