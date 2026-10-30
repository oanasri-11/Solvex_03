"""Caregiver Link API routes (Section 5b)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.caregiver_service import (
    create_caregiver_invitation,
    get_caregiver_links_for_patient,
    revoke_caregiver_link,
    get_patients_for_caregiver,
    get_all_caregiver_links,
)
from app.schemas.caregiver import (
    CaregiverInvitationRequest,
    CaregiverInvitationResponse,
    CaregiverLinkOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["caregivers"])


# ==========================================
# Patient Endpoints (/patients/me/caregivers...)
# ==========================================

@router.post(
    "/patients/me/caregivers/invitations",
    response_model=CaregiverInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def invite_caregiver(
    invite_in: CaregiverInvitationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Invite a caregiver; needs active caregiver_access consent; returns invite code."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    try:
        link = create_caregiver_invitation(
            db,
            patient_id=current_user.patient_profile.id,
            caregiver_name=invite_in.name,
            caregiver_contact=invite_in.contact,
            scope=invite_in.scope,
            notify_reminders=invite_in.notify_reminders,
            consent_id=invite_in.consent_id,
        )
        return CaregiverInvitationResponse(
            id=link.id,
            invite_code=link.invite_code,
            patient_id=link.patient_id,
            caregiver_name=link.caregiver_name,
            scope=link.scope,
            status=link.status,
            message="Caregiver invitation code generated",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/patients/me/caregivers", response_model=List[CaregiverLinkOut])
def get_own_caregivers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """List own caregiver links."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_caregiver_links_for_patient(db, current_user.patient_profile.id)


@router.post("/patients/me/caregivers/{id}/revoke", response_model=CaregiverLinkOut)
def revoke_own_caregiver(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Revoke a caregiver link immediately."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    link = revoke_caregiver_link(db, id, revoked_by=current_user.id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver link not found")
    return link


# ==========================================
# Caregiver Endpoints (/caregiver/me/patients)
# ==========================================

@router.get("/caregiver/me/patients")
def get_linked_patients_for_caregiver(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Linked patients for the authenticated caregiver."""
    if current_user.role != "caregiver":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Caregiver role required")
    return get_patients_for_caregiver(db, current_user.id)


# ==========================================
# Doctor Endpoints (/doctor/patients/{id}/caregivers)
# ==========================================

@router.get("/doctor/patients/{id}/caregivers", response_model=List[CaregiverLinkOut])
def doctor_get_patient_caregivers(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Read-only caregiver list for doctor to interpret entered_by."""
    check_patient_access(current_user, id, db)
    return get_caregiver_links_for_patient(db, id)


# ==========================================
# Admin Endpoints (/admin/caregiver-links...)
# ==========================================

@router.get("/admin/caregiver-links", response_model=List[CaregiverLinkOut])
def admin_list_caregiver_links(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    patient_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List caregiver links across the system - Admin only."""
    return get_all_caregiver_links(db, patient_id=patient_id, status=status_filter)


@router.post("/admin/caregiver-links/{id}/revoke", response_model=CaregiverLinkOut)
def admin_revoke_caregiver_link(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Revoke caregiver link - Admin only."""
    link = revoke_caregiver_link(db, id, revoked_by=current_admin.id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver link not found")
    return link
