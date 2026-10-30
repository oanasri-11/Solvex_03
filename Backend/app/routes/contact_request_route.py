"""ContactRequest API routes (Section 18)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.contact_request_service import (
    get_contact_requests_for_doctor,
    create_doctor_contact_request,
    get_contact_request_by_id,
    update_contact_request_status,
    complete_contact_request,
)
from app.schemas.contact_request import (
    ContactRequestCreate,
    ContactRequestUpdate,
    ContactRequestOut,
)

router = APIRouter(tags=["contact_requests"])


@router.get("/doctor/me/contact-requests", response_model=List[ContactRequestOut])
def doctor_get_contact_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Active outreach task queue."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return get_contact_requests_for_doctor(
        db,
        doctor_id=current_user.doctor_profile.id,
        status=status_filter,
    )


@router.post(
    "/doctor/patients/{id}/contact-requests",
    response_model=ContactRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def doctor_initiate_contact(
    id: int,
    request_in: ContactRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Doctor-initiated contact task (F19c)."""
    check_patient_access(current_user, id, db)
    return create_doctor_contact_request(
        db,
        patient_id=id,
        doctor_id=current_user.doctor_profile.id if current_user.doctor_profile else current_user.id,
        urgency=getattr(request_in, "urgency", "routine"),
        message=request_in.message,
    )


@router.get("/contact-requests/{id}", response_model=ContactRequestOut)
def get_contact_request_drawer(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Contact task drawer detail."""
    req = get_contact_request_by_id(db, id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact request not found")
    check_patient_access(current_user, req.patient_id, db)
    return req


@router.patch("/contact-requests/{id}", response_model=ContactRequestOut)
def update_contact_request_status_route(
    id: int,
    update_in: ContactRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Transition status (e.g. open -> in_progress)."""
    req = get_contact_request_by_id(db, id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact request not found")
    check_patient_access(current_user, req.patient_id, db)
    new_status = getattr(update_in, "status", "in_progress")
    return update_contact_request_status(db, id, new_status=new_status)


@router.post("/contact-requests/{id}/complete", response_model=ContactRequestOut)
def complete_contact_task_route(
    id: int,
    outcome_review_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Resolve contact task and link to resulting CaseReview."""
    req = get_contact_request_by_id(db, id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact request not found")
    check_patient_access(current_user, req.patient_id, db)
    return complete_contact_request(db, id, outcome_review_id=outcome_review_id)
