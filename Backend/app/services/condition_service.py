"""PatientCondition service (Section 7, UCPROF, SC4, RS-7)."""

from datetime import datetime, timezone
from typing import Optional, List, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.PatientCondition import PatientCondition
from app.models.patientprofile import PatientProfile


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
