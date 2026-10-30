"""PatientHelpRequest API routes (Section 17)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_patient,
    get_current_caregiver_or_patient,
    check_patient_access,
    resolve_acting_patient_id,
)
from app.models.user import User
from app.services.help_request_service import (
    create_patient_help_request,
    get_patient_help_requests,
    get_patient_help_request_by_id,
    cancel_patient_help_request,
)
from app.schemas.help_request import (
    PatientHelpRequestCreate,
    PatientHelpRequestOut,
)

router = APIRouter(tags=["help_requests"])


@router.post(
    "/patients/me/help-requests",
    response_model=PatientHelpRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_help_request(
    request_in: PatientHelpRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Submit help request (F17); automatically generates linked ContactRequest."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="help")

    try:
        return create_patient_help_request(
            db,
            patient_id=patient_id,
            request_in=request_in,
            actor_user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/patients/me/help-requests", response_model=List[PatientHelpRequestOut])
def get_own_help_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Patient request status history."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="help")
    return get_patient_help_requests(db, patient_id)


@router.get("/help-requests/{id}", response_model=PatientHelpRequestOut)
def get_help_request_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Single help request details."""
    req = get_patient_help_request_by_id(db, id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Help request not found")
    check_patient_access(current_user, req.patient_id, db)
    return req


@router.post("/help-requests/{id}/cancel", response_model=PatientHelpRequestOut)
def cancel_help_request_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Cancel pending request before clinician pickup."""
    req = get_patient_help_request_by_id(db, id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Help request not found")
    if not current_user.patient_profile or current_user.patient_profile.id != req.patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        return cancel_patient_help_request(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
