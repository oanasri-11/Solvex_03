"""Clinical Conditions API routes (Section 7)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.condition_service import (
    create_patient_condition,
    get_patient_conditions,
    get_patient_condition_by_id,
    update_patient_condition,
    delete_patient_condition,
)
from app.schemas.condition import (
    PatientConditionCreate,
    PatientConditionUpdate,
    PatientConditionOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["conditions"])


@router.post("/doctor/patients/{id}/conditions", response_model=PatientConditionOut, status_code=status.HTTP_201_CREATED)
def doctor_add_condition(
    id: int,
    condition_in: PatientConditionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Add a coded condition; recalculates priority and target suggestion."""
    check_patient_access(current_user, id, db)
    return create_patient_condition(
        db,
        patient_id=id,
        condition_in=condition_in,
        recorded_by=current_user.id,
    )


@router.get("/doctor/patients/{id}/conditions", response_model=List[PatientConditionOut])
def doctor_list_conditions(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """List clinical conditions for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_patient_conditions(db, id)


@router.get("/patients/me/conditions", response_model=List[PatientConditionOut])
def patient_get_conditions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Read-only 'Health context' for the patient."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_patient_conditions(db, current_user.patient_profile.id)


@router.patch("/conditions/{id}", response_model=PatientConditionOut)
def doctor_update_condition(
    id: int,
    condition_in: PatientConditionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Update detail or deactivate a condition."""
    cond = get_patient_condition_by_id(db, id)
    if not cond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    check_patient_access(current_user, cond.patient_id, db)
    return update_patient_condition(db, id, condition_in)


@router.delete("/conditions/{id}", response_model=MessageResponse)
def doctor_delete_condition(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Soft delete clinical condition."""
    cond = get_patient_condition_by_id(db, id)
    if not cond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    check_patient_access(current_user, cond.patient_id, db)
    delete_patient_condition(db, id)
    return MessageResponse(message=f"Condition {id} deactivated")
