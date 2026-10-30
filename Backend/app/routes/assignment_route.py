"""DoctorPatientAssignment API routes (Section 4)."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
)
from app.models.user import User
from app.services.assignment_service import (
    create_assignment,
    get_all_assignments,
    get_assignment_by_id,
    get_doctor_patients,
    end_assignment,
)
from app.schemas.assignment import (
    DoctorPatientAssignmentCreate,
    DoctorPatientAssignmentOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["assignments"])


@router.post("/doctor-assignments", response_model=DoctorPatientAssignmentOut, status_code=status.HTTP_201_CREATED)
def admin_create_assignment(
    assignment_in: DoctorPatientAssignmentCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Link a patient to a doctor - Admin only."""
    try:
        return create_assignment(db, assignment_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/doctor-assignments", response_model=List[DoctorPatientAssignmentOut])
def admin_list_assignments(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    doctor_id: Optional[int] = Query(None),
    patient_id: Optional[int] = Query(None),
    active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List doctor-patient assignments (filters: doctor_id, patient_id, active) - Admin only."""
    return get_all_assignments(
        db,
        skip=skip,
        limit=limit,
        doctor_id=doctor_id,
        patient_id=patient_id,
        active=active,
    )


@router.get("/doctor/me/patients")
def doctor_get_assigned_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Assigned patients, lightweight list for logged-in doctor."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return get_doctor_patients(db, current_user.doctor_profile.id)


@router.post("/doctor-assignments/{id}/end", response_model=DoctorPatientAssignmentOut)
def admin_end_assignment(
    id: int,
    open_items: str = Body("transfer", embed=True),
    transfer_doctor_id: Optional[int] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """End an assignment. Open alerts, contact requests and reviews must be transferred or blocked."""
    try:
        assignment = end_assignment(
            db,
            assignment_id=id,
            open_items_action=open_items,
            transfer_doctor_id=transfer_doctor_id,
        )
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
        return assignment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
