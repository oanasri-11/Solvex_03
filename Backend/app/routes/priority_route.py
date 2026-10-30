
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.priority_service import (
    get_priority_assessment_by_id,
    get_all_priority_assessments,
)

from app.services.assignment_service import is_doctor_assigned

from app.services.patient_service import get_patient_profile_by_id

from app.schemas.priority import PriorityAssessmentOut


router = APIRouter(
    prefix="/priorities",
    tags=["Priorities"],
)


# Helper: Only doctors can access priority assessments
def _require_doctor(current_user: User) -> None:
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )

    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )


# Helper: Check doctor assignment to patient
def _require_patient_assignment(
    db: Session,
    current_user: User,
    patient_id: int,
) -> None:
    _require_doctor(current_user)

    if not is_doctor_assigned(
        db,
        current_user.doctor_profile.id,
        patient_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to doctor",
        )


# 1. List priority assessments
@router.get("/", response_model=List[PriorityAssessmentOut])
def list_priority_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_doctor(current_user)

    # If a patient is specified, verify assignment first.
    if patient_id is not None:
        _require_patient_assignment(
            db,
            current_user,
            patient_id,
        )

        return get_all_priority_assessments(
            db,
            skip=skip,
            limit=limit,
            patient_id=patient_id,
            level=level,
        )

    # Fetch only assessments belonging to assigned patients.
    # This filtering is suitable for a small hackathon dataset.
    assignments = get_all_assignments(# type: ignore
        db,
        doctor_id=current_user.doctor_profile.id,
        active=True,
    )

    allowed_patient_ids = {
        assignment.patient_id for assignment in assignments
    }

    assessments = get_all_priority_assessments(
        db,
        skip=0,
        limit=10000,
        level=level,
    )

    accessible_assessments = [
        assessment
        for assessment in assessments
        if assessment.patient_id in allowed_patient_ids
    ]

    return accessible_assessments[skip:skip + limit]


# 2. Get priority assessment by ID
@router.get("/{assessment_id}", response_model=PriorityAssessmentOut)
def get_priority_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_doctor(current_user)

    assessment = get_priority_assessment_by_id(
        db,
        assessment_id,
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Priority assessment not found",
        )

    _require_patient_assignment(
        db,
        current_user,
        assessment.patient_id,# type: ignore
    )

    return assessment


