"""PatientProfile API routes (Section 2, Section 14)."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    get_current_caregiver_or_patient,
    check_patient_access,
    resolve_acting_patient_id,
)
from app.models.user import User
from app.services.patient_service import (
    enrol_patient,
    get_all_patient_profiles,
    get_patient_profile_by_id,
    get_patient_profile_by_user_id,
    update_patient_profile,
    update_patient_target,
    get_target_history,
    get_target_suggestion,
    get_patient_summary,
    get_patient_follow_up,
    get_doctor_pre_review_summary,
    get_patient_monitoring_history,
    deactivate_patient_profile,
)
from app.services.doctor_service import get_patient_doctor_info
from app.schemas.patient import (
    PatientProfileOut,
    PatientProfileUpdate,
    PatientEnrolRequest,
    PatientSelfUpdate,
    PatientTargetUpdate,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["patients"])


# ==========================================
# Patient / Caregiver Endpoints (/patients/me/...)
# ==========================================

@router.get("/patients/me", response_model=PatientProfileOut)
def get_own_patient_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Get current acting patient profile."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="view_history")
    profile = get_patient_profile_by_id(db, patient_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return profile


@router.patch("/patients/me", response_model=PatientProfileOut)
def update_own_patient_profile(
    update_in: PatientSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Patient updates own contact details and emergency contact (no clinical fields)."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    updated = update_patient_profile(
        db,
        current_user.patient_profile.id,
        PatientProfileUpdate(**update_in.model_dump(exclude_unset=True)),
    )
    return updated


@router.get("/patients/me/follow-up")
def get_own_follow_up_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Mode, schedule owner, doctor, target, consent state."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_patient_follow_up(db, current_user.patient_profile.id)


@router.get("/patients/me/summary")
def get_own_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Patient-facing summary (F04): cycle progress, recent average vs target, plain status."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="view_trend")
    return get_patient_summary(db, patient_id)


@router.get("/patients/me/doctor")
def get_own_doctor_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Assigned doctor's name and speciality only."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_patient_doctor_info(db, current_user.patient_profile.id)


# ==========================================
# Doctor Endpoints (/doctor/patients/{id}/...)
# ==========================================

@router.get("/doctor/patients/{id}", response_model=PatientProfileOut)
def doctor_get_patient(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Patient details for assigned clinician."""
    check_patient_access(current_user, id, db)
    profile = get_patient_profile_by_id(db, id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return profile


@router.patch("/doctor/patients/{id}", response_model=PatientProfileOut)
def doctor_update_clinical_profile(
    id: int,
    profile_in: PatientProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Doctor updates clinical profile: age_band, under_treatment, clinical_context."""
    check_patient_access(current_user, id, db)
    updated = update_patient_profile(db, id, profile_in)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return updated


@router.put("/doctor/patients/{id}/target")
def doctor_set_target(
    id: int,
    target_in: PatientTargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Set individual home-BP target (SC4); creates a target record and recalculates priority."""
    check_patient_access(current_user, id, db)
    doctor_id = current_user.doctor_profile.id if current_user.doctor_profile else current_user.id
    target_record = update_patient_target(
        db,
        patient_id=id,
        systolic=target_in.systolic,
        diastolic=target_in.diastolic,
        doctor_id=doctor_id,
        reason_code=target_in.reason_code,
        note=target_in.note,
    )
    return {
        "status": "target_updated",
        "patient_id": id,
        "target_systolic": target_record.systolic,
        "target_diastolic": target_record.diastolic,
        "basis": target_record.basis,
        "reason_code": target_record.reason_code,
        "set_at": target_record.set_at,
    }


@router.get("/doctor/patients/{id}/target/history")
def doctor_get_target_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Past home-BP targets with reason codes."""
    check_patient_access(current_user, id, db)
    return get_target_history(db, id)


@router.get("/doctor/patients/{id}/target/suggestion")
def doctor_get_target_suggestion(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Suggested home target and reasons from profile under active RuleVersion."""
    check_patient_access(current_user, id, db)
    return get_target_suggestion(db, id)


@router.get("/doctor/patients/{id}/summary")
def doctor_get_pre_review_summary(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Pre-review clinical digest (D3/F18): delta, active alerts, 722 completeness, quality flags."""
    check_patient_access(current_user, id, db)
    return get_doctor_pre_review_summary(db, id)


@router.get("/doctor/patients/{id}/monitoring-history")
def doctor_get_monitoring_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Longitudinal timeline combining mode changes, medication adjustments, alert events."""
    check_patient_access(current_user, id, db)
    return get_patient_monitoring_history(db, id)


# ==========================================
# Administrator Endpoints (/patients)
# ==========================================

@router.post("/patients", response_model=PatientProfileOut, status_code=status.HTTP_201_CREATED)
def admin_enrol_patient(
    enrol_in: PatientEnrolRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Enrol a patient: creates user and profile. Admin only."""
    try:
        return enrol_patient(db, enrol_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/patients", response_model=List[PatientProfileOut])
def admin_list_patients(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    enrolment_status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List all patients (filters: enrolment_status, is_active) - Admin only."""
    return get_all_patient_profiles(
        db,
        skip=skip,
        limit=limit,
        enrolment_status=enrolment_status,
        is_active=is_active,
    )


@router.delete("/patients/{id}", response_model=MessageResponse)
def admin_deactivate_patient(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Deactivate patient (soft) - Admin only."""
    success = deactivate_patient_profile(db, id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return MessageResponse(message=f"Patient {id} deactivated successfully")
