<<<<<<< HEAD
"""Patient service.

CRUD operations for the PatientProfile model, following classic SQLAlchemy syntax.
Deactivation is performed through the linked User record (soft delete only).
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
=======
"""PatientProfile service (Section 2, UC04, UC18, UCENR, UCTGT, SC4, F04, F18, RS-12)."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.models.patientprofile import PatientProfile
from app.models.user import User
<<<<<<< HEAD
from app.schemas.patient import PatientProfileCreate, PatientProfileUpdate, PatientProfileOut


def create_patient_profile(db: Session, profile_in: PatientProfileCreate) -> Optional[PatientProfile]:
    """Create a new patient profile linked to an existing user."""
    try:
        user = db.query(User).filter(User.id == profile_in.user_id).first()
        if not user:
            return None
        existing = (
            db.query(PatientProfile)
            .filter(PatientProfile.user_id == profile_in.user_id)
            .first()
        )
        if existing:
            return existing
        db_profile = PatientProfile(
            user_id=profile_in.user_id,
            date_of_birth=getattr(profile_in, "date_of_birth", None),
            gender=getattr(profile_in, "gender", None),
            phone=getattr(profile_in, "phone", None),
            address=getattr(profile_in, "address", None),
            emergency_contact_name=getattr(profile_in, "emergency_contact_name", None),
            emergency_contact_phone=getattr(profile_in, "emergency_contact_phone", None),
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError:
        db.rollback()
        raise


def get_patient_profile_by_id(db: Session, profile_id: int) -> Optional[PatientProfile]:
    """Retrieve a patient profile by its primary key."""
    return db.query(PatientProfile).filter(PatientProfile.id == profile_id).first()


def get_patient_profile_by_user_id(db: Session, user_id: int) -> Optional[PatientProfile]:
    """Retrieve a patient profile by the linked user id."""
=======
from app.models.TargetRecord import TargetRecord
from app.models.BloodPressureReading import BloodPressureReading
from app.models.Alert import Alert
from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.doctorprofile import DoctorProfile
from app.models.Consent import Consent
from app.models.PatientMonitoringMode import PatientMonitoringMode
from app.models.PatientCondition import PatientCondition
from app.models.TreatmentEvent import TreatmentEvent
from app.core.security import hash_password


def enrol_patient(db: Session, patient_in: Any, enrolled_by: Optional[int] = None) -> PatientProfile:
    """Enrol a patient (UCENR): creates user (if needed) and profile. Status is 'draft' until consent and mode exist (NCONS)."""
    user_id = getattr(patient_in, "user_id", None)
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found")
    else:
        email = getattr(patient_in, "email", None)
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required for enrolment")
        user = db.query(User).filter(User.email == email).first()
        if user:
            user_id = user.id
        else:
            raw_password = getattr(patient_in, "password", "Password123!")
            user = User(
                email=email,
                phone=getattr(patient_in, "phone", None),
                hashed_password=hash_password(raw_password),
                full_name=getattr(patient_in, "full_name", ""),
                role="patient",
                is_active=True,
            )
            db.add(user)
            db.flush()
            user_id = user.id

    existing = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient profile already exists")

    age_band = getattr(patient_in, "age_band", None)
    if not age_band and getattr(patient_in, "date_of_birth", None):
        dob = patient_in.date_of_birth
        years = (datetime.now().date() - dob).days // 365
        if years >= 80:
            age_band = "80+"
        elif years >= 65:
            age_band = "65-79"
        elif years >= 40:
            age_band = "40-64"
        else:
            age_band = "18-39"

    # Default home target based on age band (RS-12)
    default_sbp = 140 if age_band == "80+" else 135
    default_dbp = 90 if age_band == "80+" else 85

    fn = getattr(patient_in, "first_name", None)
    ln = getattr(patient_in, "last_name", None)
    if not fn and getattr(user, "full_name", None):
        parts = user.full_name.strip().split(" ", 1)
        fn = parts[0]
        ln = parts[1] if len(parts) > 1 else ""

    profile = PatientProfile(
        user_id=user_id,
        first_name=fn,
        last_name=ln,
        date_of_birth=getattr(patient_in, "date_of_birth", None),
        gender=getattr(patient_in, "gender", None),
        phone=getattr(patient_in, "phone", None) or getattr(user, "phone", None),
        address=getattr(patient_in, "address", None),
        emergency_contact_name=getattr(patient_in, "emergency_contact_name", None),
        emergency_contact_phone=getattr(patient_in, "emergency_contact_phone", None),
        age_band=age_band or "40-64",
        under_treatment=getattr(patient_in, "under_treatment", False),
        clinical_context=getattr(patient_in, "clinical_context", None),
        target_systolic=default_sbp,
        target_diastolic=default_dbp,
        target_basis="home_average",
        target_set_by=enrolled_by,
        target_set_at=datetime.now(timezone.utc),
        enrolment_status="draft",
        is_active=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def check_and_complete_enrolment(db: Session, patient_id: int) -> bool:
    """Check if patient has recorded consent and monitoring mode (NCONS). If so, sets enrolment_status = complete."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        return False

    has_consent = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.withdrawn_at.is_(None)
    ).first() is not None

    has_mode = db.query(PatientMonitoringMode).filter(
        PatientMonitoringMode.patient_id == patient_id,
        PatientMonitoringMode.ended_at.is_(None)
    ).first() is not None

    if has_consent and has_mode:
        patient.enrolment_status = "complete"
        db.commit()
        return True
    return False


def update_patient_target(
    db: Session,
    patient_id: int,
    systolic: int,
    diastolic: int,
    reason_code: Optional[str] = None,
    note: Optional[str] = None,
    doctor_user_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
) -> TargetRecord:
    doc_id = doctor_id if doctor_id is not None else (doctor_user_id if doctor_user_id is not None else 1)
    """Set individual home-BP target (SC4, RS-12). Basis is always home_average."""
    # Bounds check: SBP 100-180, DBP 60-110, SBP > DBP
    if not (100 <= systolic <= 180) or not (60 <= diastolic <= 110) or systolic <= diastolic:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="TARGET_OUT_OF_RANGE: Target values must be within safe physiological bounds (SBP 100-180, DBP 60-110, SBP > DBP)"
        )

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    now = datetime.now(timezone.utc)
    patient.target_systolic = systolic
    patient.target_diastolic = diastolic
    patient.target_basis = "home_average"
    patient.target_set_by = doctor_user_id
    patient.target_set_at = now

    record = TargetRecord(
        patient_id=patient_id,
        systolic=systolic,
        diastolic=diastolic,
        basis="home_average",
        reason_code=reason_code,
        note=note,
        set_by=doc_id,
        set_at=now,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    return record


def get_target_suggestion(db: Session, patient_id: int) -> Dict[str, Any]:
    """Suggest home target and clinical reasons based on profile (RS-12)."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    conditions = db.query(PatientCondition).filter(
        PatientCondition.patient_id == patient_id,
        PatientCondition.is_active == True  # noqa: E712
    ).all()
    cond_names = [c.condition_name.lower() for c in conditions]

    reasons = []
    # Baseline guideline (RS-12):
    # Standard home BP target: < 135/85 mmHg
    # Frail / Age 80+: < 140/90 mmHg (avoid over-treatment)
    if patient.age_band == "80+" or any("frailty" in c for c in cond_names):
        suggested_sbp = 140
        suggested_dbp = 90
        reasons.append("Age 80+ or frailty: target relaxed to <140/90 to minimize hypotension / fall risks (RS-12).")
    elif any("diabetes" in c for c in cond_names) or any("ckd" in c for c in cond_names):
        suggested_sbp = 130
        suggested_dbp = 80
        reasons.append("Diabetes or CKD: tighter home control (<130/80) considered if well-tolerated.")
    else:
        suggested_sbp = 135
        suggested_dbp = 85
        reasons.append("Standard guideline home BP target is <135/85 mmHg.")

    return {
        "patient_id": patient_id,
        "suggested_target": {
            "systolic": suggested_sbp,
            "diastolic": suggested_dbp,
            "basis": "home_average"
        },
        "current_target": {
            "systolic": patient.target_systolic or 135,
            "diastolic": patient.target_diastolic or 85,
        },
        "reasons": reasons,
        "disclaimer": "Suggestion only under active RuleVersion. Clinician decides individual target."
    }


def get_target_history(db: Session, patient_id: int) -> List[TargetRecord]:
    """List historical targets for patient."""
    return db.query(TargetRecord).filter(
        TargetRecord.patient_id == patient_id
    ).order_by(TargetRecord.set_at.desc()).all()


def get_patient_summary(db: Session, patient_id: int) -> Dict[str, Any]:
    """Patient-facing summary (UC04, F04): current cycle progress, recent average vs target, plain-language status."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    from app.services.schedule_service import get_current_cycle_progress
    cycle_progress = get_current_cycle_progress(db, patient_id)

    # 14-day average
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
    readings = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient_id,
        BloodPressureReading.measured_at >= fourteen_days_ago,
        BloodPressureReading.verification_status != "rejected"
    ).all()

    avg_sbp = round(sum(r.systolic for r in readings) / len(readings), 1) if readings else None
    avg_dbp = round(sum(r.diastolic for r in readings) / len(readings), 1) if readings else None

    target_sbp = patient.target_systolic or 135
    target_dbp = patient.target_diastolic or 85

    if avg_sbp is not None and avg_dbp is not None:
        if avg_sbp <= target_sbp and avg_dbp <= target_dbp:
            plain_status = "On Target - Great Job!"
        elif avg_sbp <= target_sbp + 5 and avg_dbp <= target_dbp + 5:
            plain_status = "Slightly Above Target"
        else:
            plain_status = "Above Target - Discuss with your doctor"
    else:
        plain_status = "No recent measurements taken"

    return {
        "patient_id": patient_id,
        "plain_language_status": plain_status,
        "target": {"systolic": target_sbp, "diastolic": target_dbp},
        "fourteen_day_average": {"systolic": avg_sbp, "diastolic": avg_dbp} if avg_sbp else None,
        "total_readings_last_14d": len(readings),
        "cycle_progress": cycle_progress,
    }


def get_doctor_pre_review_summary(db: Session, patient_id: int) -> Dict[str, Any]:
    """Pre-review clinical digest (UC18, D3/F18)."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    from app.services.schedule_service import get_current_cycle_progress
    from app.services.slot_service import calculate_adherence
    from app.services.priority_service import get_patient_priority_breakdown

    cycle_info = get_current_cycle_progress(db, patient_id)
    adherence = calculate_adherence(db, patient_id, from_date=datetime.now(timezone.utc) - timedelta(days=30))
    priority_breakdown = get_patient_priority_breakdown(db, patient_id)

    # Active alerts
    alerts = db.query(Alert).filter(
        Alert.patient_id == patient_id,
        Alert.lifecycle.in_(["raised", "delivered", "escalated"])
    ).all()

    # Data quality prompts
    recent_readings = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient_id
    ).order_by(BloodPressureReading.measured_at.desc()).limit(20).all()

    quality_prompts = []
    for r in recent_readings:
        if r.data_quality_flags:
            quality_prompts.append({
                "reading_id": r.id,
                "measured_at": r.measured_at.isoformat(),
                "flags": r.data_quality_flags,
            })

    # Medications
    medications = db.query(TreatmentEvent).filter(
        TreatmentEvent.patient_id == patient_id
    ).order_by(TreatmentEvent.effective_date.desc()).all()

    return {
        "patient_id": patient_id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "age_band": patient.age_band,
        "under_treatment": patient.under_treatment,
        "target": {"systolic": patient.target_systolic, "diastolic": patient.target_diastolic},
        "priority": priority_breakdown,
        "cycle_progress": cycle_info,
        "adherence_30d": adherence,
        "active_alerts_count": len(alerts),
        "data_quality_prompts": quality_prompts,
        "recent_medication_events": len(medications),
    }


def get_patient_follow_up(db: Session, patient_id: int) -> Dict[str, Any]:
    """Follow-up summary for patient: mode, schedule owner, doctor, target, consent state."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    from app.services.monitoring_mode_service import get_current_monitoring_mode
    mode = get_current_monitoring_mode(db, patient_id)

    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).first()

    doctor_info = None
    if assignment:
        doc = db.query(DoctorProfile).filter(DoctorProfile.id == assignment.doctor_id).first()
        if doc:
            doctor_info = {
                "name": f"Dr. {doc.first_name or ''} {doc.last_name or ''}".strip(),
                "speciality": doc.speciality or doc.specialization,
            }

    consents = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.withdrawn_at.is_(None)
    ).all()

    return {
        "patient_id": patient_id,
        "monitoring_mode": mode,
        "schedule_owner": "doctor" if mode == "telemonitoring" else "patient",
        "assigned_doctor": doctor_info,
        "target": {"systolic": patient.target_systolic, "diastolic": patient.target_diastolic},
        "active_consents": [c.type for c in consents],
        "enrolment_status": patient.enrolment_status,
    }


def get_patient_monitoring_history(db: Session, patient_id: int) -> List[Dict[str, Any]]:
    """Longitudinal timeline combining mode changes, medication adjustments, and alert events."""
    events = []

    # Alerts
    alerts = db.query(Alert).filter(Alert.patient_id == patient_id).all()
    for a in alerts:
        events.append({
            "type": "alert",
            "timestamp": a.created_at.isoformat() if a.created_at else None,
            "description": f"Alert {a.tier}: {a.message}",
        })

    # Mode changes
    modes = db.query(PatientMonitoringMode).filter(PatientMonitoringMode.patient_id == patient_id).all()
    for m in modes:
        events.append({
            "type": "mode_change",
            "timestamp": m.started_at.isoformat() if m.started_at else None,
            "description": f"Monitoring mode changed to {m.mode}. Reason: {m.reason or 'N/A'}",
        })

    # Treatment events
    treatments = db.query(TreatmentEvent).filter(TreatmentEvent.patient_id == patient_id).all()
    for t in treatments:
        events.append({
            "type": "treatment",
            "timestamp": t.effective_date.isoformat() if t.effective_date else None,
            "description": f"Medication {t.event_type}: {t.drug_name} {t.dose}",
        })

    events.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return events


def get_patient_profile_by_id(db: Session, patient_id: int) -> Optional[PatientProfile]:
    """Retrieve patient profile by ID."""
    return db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()


def get_patient_profile_by_user_id(db: Session, user_id: int) -> Optional[PatientProfile]:
    """Retrieve patient profile by User ID."""
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    return db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()


def get_all_patient_profiles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
<<<<<<< HEAD
    is_active: Optional[bool] = None,
):
    """List patient profiles with an optional is_active filter."""
    query = db.query(PatientProfile)
    if is_active is not None:
        query = query.join(User, PatientProfile.user_id == User.id).filter(
            User.is_active == is_active
        )
    return query.offset(skip).limit(limit).all()


def update_patient_profile(
    db: Session, profile_id: int, profile_in: PatientProfileUpdate
) -> Optional[PatientProfile]:
    """Update contact details and preferences of a patient profile."""
    try:
        db_profile = get_patient_profile_by_id(db, profile_id)
        if not db_profile:
            return None
        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError:
        db.rollback()
        raise


def deactivate_patient_profile(db: Session, profile_id: int) -> Optional[PatientProfile]:
    """Soft deactivate a patient by deactivating its linked user (keeps all data)."""
    try:
        db_profile = get_patient_profile_by_id(db, profile_id)
        if not db_profile:
            return None
        db_user = db.query(User).filter(User.id == db_profile.user_id).first()
        if db_user:
            db_user.is_active = False# type: ignore
            db.add(db_user)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError:
        db.rollback()
        raise
=======
    enrolment_status: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> List[PatientProfile]:
    """List patient profiles."""
    query = db.query(PatientProfile)
    if enrolment_status:
        query = query.filter(PatientProfile.enrolment_status == enrolment_status)
    if is_active is not None:
        query = query.filter(PatientProfile.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def update_patient_profile(db: Session, patient_id: int, update_data: Any) -> Optional[PatientProfile]:
    """Update profile fields."""
    profile = get_patient_profile_by_id(db, patient_id)
    if not profile:
        return None
    for field, val in update_data.dict(exclude_unset=True).items():
        if hasattr(profile, field):
            setattr(profile, field, val)
    db.commit()
    db.refresh(profile)
    return profile


def deactivate_patient_profile(db: Session, patient_id: int) -> Optional[PatientProfile]:
    """Soft deactivate patient profile."""
    profile = get_patient_profile_by_id(db, patient_id)
    if not profile:
        return None
    profile.is_active = False
    db.commit()
    db.refresh(profile)
    return profile
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
