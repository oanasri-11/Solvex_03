<<<<<<< HEAD


from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
=======
"""PatientCondition service (Section 7, UCPROF, SC4, RS-7)."""

from datetime import datetime, timezone
from typing import Optional, List, Any

from fastapi import HTTPException, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.models.PatientCondition import PatientCondition
from app.models.patientprofile import PatientProfile
<<<<<<< HEAD
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
        db_condition.is_active = False# type: ignore
        db.add(db_condition)
        db.commit()
        db.refresh(db_condition)
        return db_condition
    except SQLAlchemyError:
        db.rollback()
        raise
=======


VALID_CONDITION_CODES = {"diabetes", "ckd", "prior_cvd", "frailty", "pregnancy_postpartum", "other"}


def create_patient_condition(
    db: Session,
    condition_in: Any,
    patient_id: Optional[int] = None,
    recorded_by: Optional[int] = None,
) -> PatientCondition:
    """Add a coded condition; recalculates priority and target suggestion."""
    patient_id = patient_id or getattr(condition_in, "patient_id", None)
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    cond_name = getattr(condition_in, "condition_name", None) or getattr(condition_in, "code", None) or "other"
    cond_code = str(cond_name).lower().strip()

    cond = PatientCondition(
        patient_id=patient_id,
        condition_name=cond_code,
        diagnosed_at=getattr(condition_in, "diagnosed_at", None),
        notes=getattr(condition_in, "notes", None) or getattr(condition_in, "detail", None),
        is_active=True,
    )
    db.add(cond)
    db.commit()
    db.refresh(cond)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    return cond


def get_patient_conditions(db: Session, patient_id: int) -> List[PatientCondition]:
    """List active conditions for patient."""
    return db.query(PatientCondition).filter(
        PatientCondition.patient_id == patient_id,
        PatientCondition.is_active == True  # noqa: E712
    ).all()


def get_all_patient_conditions(db: Session, skip: int = 0, limit: int = 100) -> List[PatientCondition]:
    """List all conditions."""
    return db.query(PatientCondition).offset(skip).limit(limit).all()


def get_patient_condition_by_id(db: Session, condition_id: int) -> Optional[PatientCondition]:
    """Retrieve condition by ID."""
    return db.query(PatientCondition).filter(PatientCondition.id == condition_id).first()


def update_patient_condition(db: Session, condition_id: int, condition_update: Any) -> Optional[PatientCondition]:
    """Update condition detail or status."""
    cond = get_patient_condition_by_id(db, condition_id)
    if not cond:
        return None
    for field, val in condition_update.dict(exclude_unset=True).items():
        if hasattr(cond, field):
            setattr(cond, field, val)
    db.commit()
    db.refresh(cond)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, cond.patient_id)
    except Exception:
        pass

    return cond


def delete_patient_condition(db: Session, condition_id: int) -> Optional[PatientCondition]:
    """Soft delete condition."""
    cond = get_patient_condition_by_id(db, condition_id)
    if not cond:
        return None
    cond.is_active = False
    db.commit()
    db.refresh(cond)

    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, cond.patient_id)
    except Exception:
        pass

    return cond
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
