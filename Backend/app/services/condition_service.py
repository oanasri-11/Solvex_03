"""Condition service.

CRUD operations for the PatientCondition model, following classic SQLAlchemy syntax.
Deletion is a soft delete (is_active = False); clinical data is never hard-deleted.
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.PatientCondition import PatientCondition
from app.models.PatientProfile import PatientProfile
from app.schemas.condition import (
    PatientConditionCreate,
    PatientConditionUpdate,
    PatientConditionOut,
)


def create_patient_condition(db: Session, condition_in: PatientConditionCreate) -> Optional[PatientCondition]:
    """Add a condition for a patient. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == condition_in.patient_id).first()
        )
        if not patient:
            return None
        is_active_val = getattr(condition_in, "is_active", True)
        if is_active_val is None:
            is_active_val = True
        db_condition = PatientCondition(
            patient_id=condition_in.patient_id,
            condition_name=condition_in.condition_name,
            diagnosed_at=getattr(condition_in, "diagnosed_at", None),
            notes=getattr(condition_in, "notes", None),
            is_active=is_active_val,
        )
        db.add(db_condition)
        db.commit()
        db.refresh(db_condition)
        return db_condition
    except SQLAlchemyError:
        db.rollback()
        raise


def get_patient_condition_by_id(db: Session, condition_id: int) -> Optional[PatientCondition]:
    """Retrieve a condition by its primary key."""
    return (
        db.query(PatientCondition).filter(PatientCondition.id == condition_id).first()
    )


def get_all_patient_conditions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    """List conditions with optional patient_id / is_active filters."""
    query = db.query(PatientCondition)
    if patient_id is not None:
        query = query.filter(PatientCondition.patient_id == patient_id)
    if is_active is not None:
        query = query.filter(PatientCondition.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def update_patient_condition(
    db: Session, condition_id: int, condition_in: PatientConditionUpdate
) -> Optional[PatientCondition]:
    """Update an existing condition."""
    try:
        db_condition = get_patient_condition_by_id(db, condition_id)
        if not db_condition:
            return None
        update_data = condition_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_condition, field, value)
        db.add(db_condition)
        db.commit()
        db.refresh(db_condition)
        return db_condition
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_patient_condition(db: Session, condition_id: int) -> Optional[PatientCondition]:
    """Soft delete a condition (is_active = False). Clinical data is kept."""
    try:
        db_condition = get_patient_condition_by_id(db, condition_id)
        if not db_condition:
            return None
        db_condition.is_active = False
        db.add(db_condition)
        db.commit()
        db.refresh(db_condition)
        return db_condition
    except SQLAlchemyError:
        db.rollback()
        raise
