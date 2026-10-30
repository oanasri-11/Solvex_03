"""Treatment Events API routes (Section 7b)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.treatment_event_service import (
    record_treatment_event,
    get_treatment_events,
    get_current_medications,
    correct_treatment_event,
)
from app.schemas.treatment_event import (
    TreatmentEventCreate,
    TreatmentEventCorrect,
    TreatmentEventOut,
    CurrentMedicationsOut,
)

router = APIRouter(tags=["treatment_events"])


@router.post(
    "/doctor/patients/{id}/treatment-events",
    response_model=TreatmentEventOut,
    status_code=status.HTTP_201_CREATED,
)
def doctor_record_treatment_event(
    id: int,
    event_in: TreatmentEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Record a treatment event; opens post-change comparison window; recalculates priority."""
    check_patient_access(current_user, id, db)
    return record_treatment_event(
        db,
        patient_id=id,
        event_in=event_in,
        recorded_by=current_user.id,
    )


@router.get("/doctor/patients/{id}/treatment-events", response_model=List[TreatmentEventOut])
def doctor_get_treatment_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Treatment event history for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_treatment_events(db, id)


@router.get("/doctor/patients/{id}/medications/current", response_model=CurrentMedicationsOut)
def doctor_get_current_medications(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Derived current medication list and number of antihypertensive classes."""
    check_patient_access(current_user, id, db)
    return get_current_medications(db, id)


@router.post("/treatment-events/{id}/correct", response_model=TreatmentEventOut)
def doctor_correct_treatment_event(
    id: int,
    correction_in: TreatmentEventCorrect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Correction as a new event that references the old one (immutable history)."""
    try:
        return correct_treatment_event(
            db,
            original_event_id=id,
            correction_in=correction_in,
            recorded_by=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
