"""Caregiver service (Section 5b, NCGV)."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.CaregiverLink import CaregiverLink
from app.models.Consent import Consent
from app.models.patientprofile import PatientProfile


VALID_CAREGIVER_SCOPES = {"record", "confirm_slot", "view_history", "view_trend", "reminders", "help"}


def create_caregiver_invitation(
    db: Session,
    patient_id: int,
    name: str = "",
    contact: str = "",
    scope: Optional[List[str]] = None,
    consent_id: Optional[int] = None,
    caregiver_name: Optional[str] = None,
    caregiver_contact: Optional[str] = None,
    notify_reminders: bool = False,
) -> CaregiverLink:
    name = caregiver_name or name
    contact = caregiver_contact or contact
    scope = scope or ["record", "view_history", "view_trend"]
    """Invite a caregiver (NCGV). Requires active caregiver_access consent."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    # Validate scopes
    for s in scope:
        if s not in VALID_CAREGIVER_SCOPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid scope '{s}'")

    # Consent check
    consent = None
    if consent_id:
        consent = db.query(Consent).filter(Consent.id == consent_id, Consent.patient_id == patient_id).first()
    else:
        consent = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.type == "caregiver_access",
            Consent.withdrawn_at.is_(None)
        ).first()

    if not consent:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CONSENT_REQUIRED: Patient must grant active caregiver_access consent first"
        )

    invite_code = f"INV-{uuid.uuid4().hex[:10].upper()}"

    link = CaregiverLink(
        patient_id=patient_id,
        caregiver_name=name,
        caregiver_contact=contact,
        invite_code=invite_code,
        scope=scope,
        status="invited",
        consent_id=consent.id if consent else None,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def accept_caregiver_invitation(db: Session, invite_code: str, caregiver_user_id: int) -> CaregiverLink:
    """Caregiver accepts invite with registration code."""
    link = db.query(CaregiverLink).filter(
        CaregiverLink.invite_code == invite_code,
        CaregiverLink.status == "invited"
    ).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired caregiver invite code")

    link.caregiver_user_id = caregiver_user_id
    link.status = "active"
    db.commit()
    db.refresh(link)
    return link


def get_caregiver_links_for_patient(db: Session, patient_id: int) -> List[CaregiverLink]:
    """List caregiver links for patient."""
    return db.query(CaregiverLink).filter(
        CaregiverLink.patient_id == patient_id,
        CaregiverLink.status != "revoked"
    ).all()


def get_patients_for_caregiver(db: Session, caregiver_user_id: int) -> List[Dict[str, Any]]:
    """List linked patients for a caregiver."""
    links = db.query(CaregiverLink).filter(
        CaregiverLink.caregiver_user_id == caregiver_user_id,
        CaregiverLink.status == "active"
    ).all()

    result = []
    for l in links:
        patient = db.query(PatientProfile).filter(PatientProfile.id == l.patient_id).first()
        if patient:
            result.append({
                "link_id": l.id,
                "patient_id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "scope": l.scope,
                "status": l.status,
            })
    return result


def revoke_caregiver_link(
    db: Session,
    link_id: int,
    actor_id: Optional[int] = None,
    revoked_by: Optional[int] = None,
) -> CaregiverLink:
    actor_id = revoked_by or actor_id or 1
    """Revoke caregiver access link immediately."""
    link = db.query(CaregiverLink).filter(CaregiverLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver link not found")

    link.status = "revoked"
    link.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(link)
    return link


def get_all_caregiver_links(
    db: Session,
    patient_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    status: Optional[str] = None,
) -> List[CaregiverLink]:
    status_filter = status or status_filter
    """Admin query of all caregiver links."""
    query = db.query(CaregiverLink)
    if patient_id is not None:
        query = query.filter(CaregiverLink.patient_id == patient_id)
    if status_filter:
        query = query.filter(CaregiverLink.status == status_filter)
    return query.all()
