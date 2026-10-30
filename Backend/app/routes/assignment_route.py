
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    check_patient_access,
    
)
from app.models.user import User

from app.services.assignment_service import (
    create_assignment,
    get_assignment_by_id,
    get_all_assignments,
    update_assignment,
    end_assignment,
    is_doctor_assigned,
)

from app.schemas.assignment import (
    DoctorPatientAssignmentCreate,
    DoctorPatientAssignmentUpdate,
    DoctorPatientAssignmentOut,
)


router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("/", response_model=List[DoctorPatientAssignmentOut])
def list_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    doctor_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None),
    active: Optional[bool] = Query(None),
):
    """List assignments with optional filters."""

    if current_user.role == "patient":# type: ignore
        if not current_user.patient_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found",
            )
        patient_id = current_user.patient_profile.id

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )
        doctor_id = current_user.doctor_profile.id

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view assignments",
        )

    return get_all_assignments(
        db,
        skip=skip,
        limit=limit,
        doctor_id=doctor_id,
        patient_id=patient_id,
        active=active,
    )


@router.get("/check/{doctor_id}/{patient_id}", response_model=bool)
def check_assignment_route(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check whether a doctor is actively assigned to a patient."""

    if current_user.role == "patient":# type: ignore
        check_patient_access(current_user, patient_id, db)# type: ignore

    elif current_user.role == "doctor":# type: ignore
        if (
            not current_user.doctor_profile
            or current_user.doctor_profile.id != doctor_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only check their own assignments",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check assignments",
        )

    return is_doctor_assigned(db, doctor_id, patient_id)


@router.get("/{assignment_id}", response_model=DoctorPatientAssignmentOut)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get an assignment by ID."""

    assignment = get_assignment_by_id(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if current_user.role == "patient":# type: ignore
        check_patient_access(current_user, assignment.patient_id, db) # type: ignore

    elif current_user.role == "doctor":# type: ignore
        if (
            not current_user.doctor_profile
            or current_user.doctor_profile.id != assignment.doctor_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this assignment",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this assignment",
        )

    return assignment


@router.post(
    "/",
    response_model=DoctorPatientAssignmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment_route(
    assignment_in: DoctorPatientAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Link a patient to a doctor."""

    if current_user.role != "doctor": # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors may create assignments",
        )

    if (
        not current_user.doctor_profile
        or current_user.doctor_profile.id != assignment_in.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors may only create assignments for themselves",
        )

    assignment = create_assignment(db, assignment_in)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor or patient profile not found",
        )

    return assignment


@router.put("/{assignment_id}", response_model=DoctorPatientAssignmentOut)
def update_assignment_route(
    assignment_id: int,
    assignment_in: DoctorPatientAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an assignment (assigned doctor only)."""

    assignment = get_assignment_by_id(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if (
        current_user.role != "doctor" # type: ignore
        or not current_user.doctor_profile # type: ignore
        or current_user.doctor_profile.id != assignment.doctor_id # type: ignore
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this assignment",
        )

    updated = update_assignment(db, assignment_id, assignment_in)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return updated


@router.post("/{assignment_id}/end", response_model=DoctorPatientAssignmentOut)
def end_assignment_route(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """End (deactivate) an assignment (assigned doctor only)."""

    assignment = get_assignment_by_id(db, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    if (
        current_user.role != "doctor"  # type: ignore
        or not current_user.doctor_profile
        or current_user.doctor_profile.id != assignment.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to end this assignment",
        )

    ended = end_assignment(db, assignment_id)

    if not ended:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return ended



