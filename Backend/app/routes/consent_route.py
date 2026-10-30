"""Consent API routes (Section 6, SC5)."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    get_current_user_any,
    check_patient_access,
)
from app.models.user import User
from app.services.consent_service import (
    get_current_consent_text,
    record_consent,
    get_patient_consents,
    get_effective_consent_state,
    withdraw_consent,
)
from app.schemas.consent import (
    ConsentCreate,
    ConsentAdminCreate,
    ConsentOut,
    ConsentStateOut,
)

router = APIRouter(tags=["consents"])


@router.get("/consent-texts/current")
def get_active_consent_text(
    lang: Optional[str] = Header("fr", alias="Accept-Language"),
):
    """Current consent text in FR or AR with its version."""
    return get_current_consent_text()


# ==========================================
# Patient Endpoints (/patients/me/consents...)
# ==========================================

@router.post("/patients/me/consents", response_model=ConsentOut, status_code=status.HTTP_201_CREATED)
def patient_record_consent(
    consent_in: ConsentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Record consent (data_sharing, monitoring_mode, caregiver_access)."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    try:
        return record_consent(
            db,
            patient_id=current_user.patient_profile.id,
            consent_type=consent_in.type,
            text_version=consent_in.text_version,
            recorded_by=current_user.id,
            method="in_app",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/patients/me/consents", response_model=List[ConsentOut])
def patient_get_consent_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Own consent history."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_patient_consents(db, current_user.patient_profile.id)


@router.get("/patients/me/consents/state", response_model=ConsentStateOut)
def patient_get_effective_consent_state(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Effective state per consent type."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_effective_consent_state(db, current_user.patient_profile.id)


@router.post("/patients/me/consents/{id}/withdraw", response_model=ConsentOut)
def patient_withdraw_consent(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Withdraw consent; flags case for doctor; no automatic data deletion."""
    consent = withdraw_consent(db, consent_id=id, user_id=current_user.id)
    if not consent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent record not found")
    return consent


# ==========================================
# Doctor Endpoints (/doctor/patients/{id}/consents)
# ==========================================

@router.get("/doctor/patients/{id}/consents", response_model=ConsentStateOut)
def doctor_get_patient_consents(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Patient consent state for assigned clinician."""
    check_patient_access(current_user, id, db)
    return get_effective_consent_state(db, id)


# ==========================================
# Admin Endpoints (/admin/patients/{id}/consents...)
# ==========================================

@router.post("/admin/patients/{id}/consents", response_model=ConsentOut, status_code=status.HTTP_201_CREATED)
def admin_record_patient_consent(
    id: int,
    consent_in: ConsentAdminCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Record consent on patient's behalf at enrolment (paper or verbal)."""
    try:
        return record_consent(
            db,
            patient_id=id,
            consent_type=consent_in.type,
            text_version=consent_in.text_version,
            recorded_by=current_admin.id,
            method=consent_in.method,
            witness_note=consent_in.witness_note,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/admin/patients/{id}/consents", response_model=List[ConsentOut])
def admin_get_patient_consent_history(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Consent history of a patient - Admin only."""
    return get_patient_consents(db, id)
