<<<<<<< HEAD


from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.PatientMonitoringMode import PatientMonitoringMode
from app.models.patientprofile import PatientProfile
from app.schemas.monitoring_mode import (
    PatientMonitoringModeCreate,
    PatientMonitoringModeUpdate,
    PatientMonitoringModeOut,
)


def create_monitoring_mode(db: Session, mode_in: PatientMonitoringModeCreate) -> Optional[PatientMonitoringMode]:
    """Record a monitoring mode for a patient."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == mode_in.patient_id).first()
        )
        if not patient:
            return None
        existing = (
            db.query(PatientMonitoringMode)
            .filter(PatientMonitoringMode.patient_id == mode_in.patient_id)
            .first()
        )
        if existing:
            existing.mode = mode_in.mode# type: ignore
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        db_mode = PatientMonitoringMode(
            patient_id=mode_in.patient_id,
            mode=mode_in.mode,
        )
        db.add(db_mode)
        db.commit()
        db.refresh(db_mode)
        return db_mode
    except SQLAlchemyError:
        db.rollback()
        raise


def get_monitoring_mode_by_id(db: Session, mode_id: int) -> Optional[PatientMonitoringMode]:
    """Retrieve a monitoring mode record by its primary key."""
    return (
        db.query(PatientMonitoringMode).filter(PatientMonitoringMode.id == mode_id).first()
    )


def get_monitoring_mode_by_patient(
    db: Session, patient_id: int
) -> Optional[PatientMonitoringMode]:
    """Retrieve the current monitoring mode for a patient."""
    return (
        db.query(PatientMonitoringMode)
        .filter(PatientMonitoringMode.patient_id == patient_id)
        .first()
    )


def get_all_monitoring_modes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
):
    """List monitoring mode records (history), optionally filtered by patient."""
    query = db.query(PatientMonitoringMode)
    if patient_id is not None:
        query = query.filter(PatientMonitoringMode.patient_id == patient_id)
    return query.offset(skip).limit(limit).all()



=======
"""PatientMonitoringMode service (Section 5, UCMODE, UCREQM, NMODE, NCONS, RS-5)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.PatientMonitoringMode import PatientMonitoringMode
from app.models.ModeChangeRequest import ModeChangeRequest
from app.models.patientprofile import PatientProfile
from app.models.Consent import Consent
from app.models.TreatmentEvent import TreatmentEvent
from app.models.MeasurementSchedule import MeasurementSchedule


def get_current_monitoring_mode(db: Session, patient_id: int) -> str:
    """Return active mode for patient (default 'self_monitoring')."""
    active = db.query(PatientMonitoringMode).filter(
        PatientMonitoringMode.patient_id == patient_id,
        PatientMonitoringMode.ended_at.is_(None)
    ).order_by(PatientMonitoringMode.started_at.desc()).first()

    return active.mode if active else "self_monitoring"


def assign_monitoring_mode(
    db: Session,
    patient_id: int,
    mode: str,
    reason: Optional[str] = None,
    consent_id: Optional[int] = None,
    doctor_user_id: Optional[int] = None,
    changed_by: Optional[int] = None,
) -> PatientMonitoringMode:
    actor_id = changed_by if changed_by is not None else (doctor_user_id if doctor_user_id is not None else 1)
    """Set or change mode (UCMODE). Requires recorded consent (NCONS). Closes previous record."""
    if mode not in ["self_monitoring", "telemonitoring"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mode must be 'self_monitoring' or 'telemonitoring'"
        )

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    # Consent verification (NCONS)
    consent = None
    if consent_id:
        consent = db.query(Consent).filter(Consent.id == consent_id, Consent.patient_id == patient_id).first()
    else:
        consent = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.withdrawn_at.is_(None)
        ).first()

    if not consent:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CONSENT_REQUIRED: Assigning a monitoring mode requires recorded patient consent"
        )

    now = datetime.now(timezone.utc)

    # Close previous mode record
    previous_modes = db.query(PatientMonitoringMode).filter(
        PatientMonitoringMode.patient_id == patient_id,
        PatientMonitoringMode.ended_at.is_(None)
    ).all()
    for pm in previous_modes:
        pm.ended_at = now

    new_mode = PatientMonitoringMode(
        patient_id=patient_id,
        mode=mode,
        started_at=now,
        changed_by=actor_id,
        consent_id=consent.id if consent else None,
        reason=reason,
    )
    db.add(new_mode)
    db.commit()
    db.refresh(new_mode)

    # Flip schedule ownership if needed (NMODE)
    active_sched = db.query(MeasurementSchedule).filter(
        MeasurementSchedule.patient_id == patient_id,
        MeasurementSchedule.is_active == True  # noqa: E712
    ).first()
    if active_sched:
        active_sched.owner = "doctor" if mode == "telemonitoring" else "patient"
        db.commit()

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    # Check enrolment completion
    try:
        from app.services.patient_service import check_and_complete_enrolment
        check_and_complete_enrolment(db, patient_id)
    except Exception:
        pass

    return new_mode


def get_mode_suitability(db: Session, patient_id: int) -> Dict[str, Any]:
    """Decision support: factors for and against telemonitoring (RS-5). Never excludes by age alone."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    from app.services.slot_service import calculate_adherence
    adherence = calculate_adherence(db, patient_id)

    # Medication classes count
    meds = db.query(TreatmentEvent).filter(
        TreatmentEvent.patient_id == patient_id,
        TreatmentEvent.event_type != "stopped"
    ).all()
    drug_classes = set(m.drug_class for m in meds)

    factors = []
    # 1. Uncontrolled BP factor
    if patient.target_systolic and patient.target_systolic < 135:
        factors.append({"factor": "Tight BP Target", "supports_telemonitoring": True, "strength": "high", "detail": "Patient requires tighter monitoring to reach target."})

    # 2. Number of antihypertensive classes
    if len(drug_classes) >= 3:
        factors.append({"factor": "Resistant / Multi-drug Hypertension", "supports_telemonitoring": True, "strength": "high", "detail": f"Patient is on {len(drug_classes)} antihypertensive classes."})
    elif len(drug_classes) == 1:
        factors.append({"factor": "Single-agent Therapy", "supports_telemonitoring": False, "strength": "medium", "detail": "Monotherapy patients often do well with self-monitoring."})

    # 3. Adherence history
    if adherence["rating"] == "poor":
        factors.append({"factor": "Low Adherence", "supports_telemonitoring": False, "strength": "medium", "detail": "Telemonitoring relies on regular transmission; self-monitoring with reminders may be less burdensome."})
    elif adherence["rating"] == "good":
        factors.append({"factor": "High Adherence", "supports_telemonitoring": True, "strength": "high", "detail": "Demonstrated reliability in logging readings."})

    # 4. Age factor (RS-5 note: never exclude by age alone)
    if patient.age_band == "80+":
        factors.append({"factor": "Age 80+", "supports_telemonitoring": True, "strength": "medium", "detail": "Older patients benefit from clinical oversight to prevent orthostatic hypotension and over-treatment."})

    return {
        "patient_id": patient_id,
        "current_mode": get_current_monitoring_mode(db, patient_id),
        "factors": factors,
        "recommendation": "Telemonitoring Recommended" if sum(1 for f in factors if f["supports_telemonitoring"]) >= 2 else "Self-Monitoring Suitable",
        "guidance": "Decision support only. Clinician and patient decide mode jointly."
    }


def request_mode_change(db: Session, patient_id: int, requested_mode: str, reason: Optional[str] = None) -> ModeChangeRequest:
    """Patient asks for a mode change (UCREQM)."""
    if requested_mode not in ["self_monitoring", "telemonitoring"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid requested mode")

    req = ModeChangeRequest(
        patient_id=patient_id,
        requested_mode=requested_mode,
        reason=reason,
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_mode_change_requests_for_patient(db: Session, patient_id: int) -> List[ModeChangeRequest]:
    """Retrieve mode requests for patient."""
    return db.query(ModeChangeRequest).filter(
        ModeChangeRequest.patient_id == patient_id
    ).order_by(ModeChangeRequest.created_at.desc()).all()


def get_pending_requests_for_doctor(db: Session, doctor_id: int, status: Optional[str] = None) -> List[ModeChangeRequest]:
    """List pending mode change requests for doctor's assigned patients."""
    from app.models.DoctorPatientAssignment import DoctorPatientAssignment
    assigned = db.query(DoctorPatientAssignment.patient_id).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).all()
    patient_ids = [a[0] for a in assigned]
    if not patient_ids:
        return []

    status_filter = status or "pending"
    query = db.query(ModeChangeRequest).filter(ModeChangeRequest.patient_id.in_(patient_ids))
    if status_filter != "all":
        query = query.filter(ModeChangeRequest.status == status_filter)
    return query.order_by(ModeChangeRequest.created_at.desc()).all()


def resolve_mode_change_request(
    db: Session,
    request_id: int,
    decision: str,
    note: Optional[str] = None,
    doctor_user_id: int = 1,
) -> ModeChangeRequest:
    """Doctor approves or declines mode change request."""
    req = db.query(ModeChangeRequest).filter(ModeChangeRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if decision not in ["approved", "declined"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Decision must be 'approved' or 'declined'")

    now = datetime.now(timezone.utc)
    req.status = decision
    req.resolved_by = doctor_user_id
    req.resolved_at = now
    req.note = note
    db.commit()

    if decision == "approved":
        assign_monitoring_mode(
            db,
            patient_id=req.patient_id,
            mode=req.requested_mode,
            reason=f"Approved patient request: {req.reason or ''}",
            doctor_user_id=doctor_user_id
        )

    return req


def get_monitoring_mode_history(db: Session, patient_id: int) -> List[PatientMonitoringMode]:
    """Retrieve full mode history."""
    return db.query(PatientMonitoringMode).filter(
        PatientMonitoringMode.patient_id == patient_id
    ).order_by(PatientMonitoringMode.started_at.desc()).all()


def get_monitoring_mode_by_id(db: Session, mode_id: int) -> Optional[PatientMonitoringMode]:
    """Get single mode record."""
    return db.query(PatientMonitoringMode).filter(PatientMonitoringMode.id == mode_id).first()


def get_all_monitoring_modes(db: Session, skip: int = 0, limit: int = 100) -> List[PatientMonitoringMode]:
    """List monitoring modes."""
    return db.query(PatientMonitoringMode).offset(skip).limit(limit).all()


def create_monitoring_mode(db: Session, mode_in: Any) -> PatientMonitoringMode:
    """Legacy helper."""
    return assign_monitoring_mode(
        db,
        patient_id=mode_in.patient_id,
        mode=getattr(mode_in, "mode", "self_monitoring"),
    )
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
