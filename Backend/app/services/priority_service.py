<<<<<<< HEAD


from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
=======
"""Priority & Triage Evaluation service (UC10, UC11, UC12, F10, F11, F12).

Formula:
Priority Score = W_alert * Tier + W_trend * DeltaBP + W_adh * (1 - Adherence) + C_risk

Factors:
- Active Alert Tier (W_alert)
- BP Delta from Target (W_trend)
- Adherence / Missed Slots (W_adh)
- Context Risk Modifier (C_risk): Diabetes, CKD, CVD, Frailty, Age 80+
- Mode-dependent rule (NMODE): self-monitoring patients are not actively triaged unless
  critical escalation reached or help requested.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.models.PriorityAssessment import PriorityAssessment
from app.models.patientprofile import PatientProfile
<<<<<<< HEAD
from app.models.user import User
from app.schemas.priority import (
    PriorityAssessmentCreate,
    PriorityAssessmentUpdate,
    PriorityAssessmentOut,
)


def create_priority_assessment(
    db: Session, assessment_in: PriorityAssessmentCreate
) -> Optional[PriorityAssessment]:
    """Backend-only creation of a priority assessment. Verifies patient and assessor."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == assessment_in.patient_id).first()
        )
        if not patient:
            return None
        if assessment_in.assessor_id is not None:
            assessor = db.query(User).filter(User.id == assessment_in.assessor_id).first()
            if not assessor:
                return None
        assessed_at = getattr(assessment_in, "assessed_at", None) or datetime.utcnow()
        db_assessment = PriorityAssessment(
            patient_id=assessment_in.patient_id,
            assessor_id=assessment_in.assessor_id,
            level=assessment_in.level,
            assessed_at=assessed_at,
            notes=getattr(assessment_in, "notes", None),
        )
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        return db_assessment
    except SQLAlchemyError:
        db.rollback()
        raise


def get_priority_assessment_by_id(
    db: Session, assessment_id: int
) -> Optional[PriorityAssessment]:
    """Retrieve a priority assessment by its primary key."""
    return (
        db.query(PriorityAssessment).filter(PriorityAssessment.id == assessment_id).first()
    )


def get_all_priority_assessments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    level: Optional[str] = None,
):
    """List priority assessments with optional patient_id / level filters."""
    query = db.query(PriorityAssessment)
    if patient_id is not None:
        query = query.filter(PriorityAssessment.patient_id == patient_id)
    if level is not None:
        query = query.filter(PriorityAssessment.level == level)
    return query.order_by(PriorityAssessment.assessed_at.desc()).offset(skip).limit(limit).all()



=======
from app.models.Alert import Alert
from app.models.BloodPressureReading import BloodPressureReading
from app.models.PatientCondition import PatientCondition
from app.models.ScheduleSlot import ScheduleSlot
from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.PatientHelpRequest import PatientHelpRequest
from app.models.PatientMonitoringMode import PatientMonitoringMode


def calculate_patient_priority(db: Session, patient_id: int) -> PriorityAssessment:
    """Calculate and persist clinical priority classification for a patient."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    reasons = []
    score = 0.0

    # 1. Monitoring Mode Check (Design Note NMODE)
    from app.services.monitoring_mode_service import get_current_monitoring_mode
    current_mode = get_current_monitoring_mode(db, patient_id)
    is_telemonitoring = (current_mode == "telemonitoring")

    # Check open help requests
    has_open_help = db.query(PatientHelpRequest).filter(
        PatientHelpRequest.patient_id == patient_id,
        PatientHelpRequest.status.in_(["open", "in_progress"])
    ).first() is not None

    # 2. Alert Factor (W_alert)
    active_alerts = db.query(Alert).filter(
        Alert.patient_id == patient_id,
        Alert.lifecycle.in_(["raised", "delivered", "escalated"])
    ).all()

    alert_score = 0.0
    top_alert_tier = "none"
    for a in active_alerts:
        if a.tier == "critical_emergency":
            alert_score = max(alert_score, 100.0)
            top_alert_tier = "critical_emergency"
            reasons.append("ACTIVE_CRITICAL_EMERGENCY_ALERT")
        elif a.tier == "severe_single_reading":
            alert_score = max(alert_score, 60.0)
            if top_alert_tier not in ["critical_emergency"]:
                top_alert_tier = "severe_single_reading"
            reasons.append("ACTIVE_SEVERE_READING_ALERT")
        elif a.tier == "persistent_elevation":
            alert_score = max(alert_score, 30.0)
            if top_alert_tier not in ["critical_emergency", "severe_single_reading"]:
                top_alert_tier = "persistent_elevation"
            reasons.append("ACTIVE_PERSISTENT_ELEVATION_ALERT")
        elif a.tier == "routine_out_of_range":
            alert_score = max(alert_score, 10.0)
            if top_alert_tier == "none":
                top_alert_tier = "routine_out_of_range"

    score += alert_score

    # 3. BP Delta Factor (W_trend)
    target_sbp = patient.target_systolic or 135
    target_dbp = patient.target_diastolic or 85
    recent_readings = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient_id,
        BloodPressureReading.verification_status != "rejected"
    ).order_by(BloodPressureReading.measured_at.desc()).limit(5).all()

    delta_sbp = 0.0
    if recent_readings:
        avg_sbp = sum(r.systolic for r in recent_readings) / len(recent_readings)
        delta_sbp = max(0.0, avg_sbp - target_sbp)
        score += delta_sbp * 1.5
        if delta_sbp >= 20:
            reasons.append("SEVERE_BP_DELTA_ABOVE_TARGET")
        elif delta_sbp >= 10:
            reasons.append("MODERATE_BP_DELTA_ABOVE_TARGET")

    # 4. Adherence Factor (W_adh)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    slots = db.query(ScheduleSlot).filter(
        ScheduleSlot.patient_id == patient_id,
        ScheduleSlot.due_at >= thirty_days_ago,
        ScheduleSlot.status.in_(["taken", "missed", "partial"])
    ).all()

    adherence_rate = 1.0
    if slots:
        taken_count = sum(1 for s in slots if s.status == "taken")
        adherence_rate = taken_count / len(slots)
        if adherence_rate < 0.6:
            score += 20.0
            reasons.append("LOW_MEASUREMENT_ADHERENCE")
        elif adherence_rate < 0.8:
            score += 10.0
            reasons.append("SUBOPTIMAL_MEASUREMENT_ADHERENCE")

    # 5. Clinical Risk Modifiers (C_risk: RS-7)
    conditions = db.query(PatientCondition).filter(
        PatientCondition.patient_id == patient_id,
        PatientCondition.is_active == True  # noqa: E712
    ).all()
    cond_codes = [c.condition_name.lower() for c in conditions]

    if any("ckd" in c for c in cond_codes):
        score += 15.0
        reasons.append("RISK_FACTOR_CKD")
    if any("diabetes" in c for c in cond_codes):
        score += 15.0
        reasons.append("RISK_FACTOR_DIABETES")
    if any("cvd" in c or "prior_cvd" in c for c in cond_codes):
        score += 15.0
        reasons.append("RISK_FACTOR_PRIOR_CVD")
    if any("frailty" in c for c in cond_codes):
        score += 10.0
        reasons.append("RISK_FACTOR_FRAILTY")
    if patient.age_band == "80+":
        score += 10.0
        reasons.append("AGE_BAND_80_PLUS")

    if has_open_help:
        score += 25.0
        reasons.append("OPEN_PATIENT_HELP_REQUEST")

    # 6. Mode & Threshold Resolution
    # Self-monitoring patients are not actively triaged unless critical or help requested
    if not is_telemonitoring and top_alert_tier != "critical_emergency" and not has_open_help:
        priority_level = "not_triaged"
        level_legacy = "low"
    else:
        if score >= 80.0 or top_alert_tier == "critical_emergency":
            priority_level = "P1_critical"
            level_legacy = "urgent"
        elif score >= 50.0 or top_alert_tier == "severe_single_reading":
            priority_level = "P2_high"
            level_legacy = "high"
        elif score >= 25.0:
            priority_level = "P3_moderate"
            level_legacy = "medium"
        else:
            priority_level = "P4_routine"
            level_legacy = "low"

    assessment = PriorityAssessment(
        patient_id=patient_id,
        priority_level=priority_level,
        level=level_legacy,
        score=round(score, 1),
        reasons=reasons,
        inputs={
            "monitoring_mode": current_mode,
            "top_alert_tier": top_alert_tier,
            "delta_sbp": round(delta_sbp, 1),
            "adherence_rate": round(adherence_rate, 2),
            "condition_count": len(conditions),
            "age_band": patient.age_band,
            "has_open_help": has_open_help,
        },
        assessed_at=datetime.now(timezone.utc),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_priority_queue(
    db: Session,
    doctor_id: int,
    search: Optional[str] = None,
    priority_level: Optional[List[str]] = None,
    alert_tier: Optional[List[str]] = None,
    monitoring_mode: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    priority_levels: Optional[List[str]] = None,
    alert_tiers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if priority_levels is not None and priority_level is None:
        priority_level = priority_levels
    if alert_tiers is not None and alert_tier is None:
        alert_tier = alert_tiers
    """Retrieve priority-sorted patient queue for doctor workspace (D1, F11, F12)."""
    assigned = db.query(DoctorPatientAssignment.patient_id).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).all()
    patient_ids = [a[0] for a in assigned]
    if not patient_ids:
        return {"items": [], "page": page, "page_size": page_size, "total": 0}

    patients = db.query(PatientProfile).filter(PatientProfile.id.in_(patient_ids)).all()

    # Get latest priority assessment per patient
    queue_items = []
    for p in patients:
        latest_pa = db.query(PriorityAssessment).filter(
            PriorityAssessment.patient_id == p.id
        ).order_by(PriorityAssessment.assessed_at.desc()).first()

        latest_reading = db.query(BloodPressureReading).filter(
            BloodPressureReading.patient_id == p.id
        ).order_by(BloodPressureReading.measured_at.desc()).first()

        active_alert = db.query(Alert).filter(
            Alert.patient_id == p.id,
            Alert.lifecycle.in_(["raised", "delivered", "escalated"])
        ).order_by(Alert.created_at.desc()).first()

        item = {
            "patient_id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "priority_level": latest_pa.priority_level if latest_pa else "P4_routine",
            "score": latest_pa.score if latest_pa else 0.0,
            "reasons": latest_pa.reasons if latest_pa else [],
            "alert_tier": active_alert.tier if active_alert else "none",
            "last_reading": {
                "systolic": latest_reading.systolic,
                "diastolic": latest_reading.diastolic,
                "measured_at": latest_reading.measured_at.isoformat() if latest_reading else None,
            } if latest_reading else None,
            "target": {
                "systolic": p.target_systolic or 135,
                "diastolic": p.target_diastolic or 85
            }
        }
        queue_items.append(item)

    # Sort items: P1_critical > P2_high > P3_moderate > P4_routine > not_triaged, then by score desc
    rank_map = {"P1_critical": 0, "P2_high": 1, "P3_moderate": 2, "P4_routine": 3, "not_triaged": 4}
    queue_items.sort(key=lambda x: (rank_map.get(x["priority_level"], 5), -x["score"]))

    # Apply filters
    if priority_level:
        queue_items = [i for i in queue_items if i["priority_level"] in priority_level]
    if alert_tier:
        queue_items = [i for i in queue_items if i["alert_tier"] in alert_tier]
    if search:
        s = search.lower()
        queue_items = [
            i for i in queue_items
            if (i["first_name"] and s in i["first_name"].lower()) or
               (i["last_name"] and s in i["last_name"].lower()) or
               s in str(i["patient_id"])
        ]

    total = len(queue_items)
    start = (page - 1) * page_size
    items_page = queue_items[start:start + page_size]

    return {
        "items": items_page,
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def get_priority_queue_updates(db: Session, doctor_id: int, since: Optional[datetime] = None) -> Dict[str, Any]:
    """Delta cursor for priority queue update badges."""
    since_dt = since or (datetime.now(timezone.utc) - timedelta(hours=24))
    assigned = db.query(DoctorPatientAssignment.patient_id).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).all()
    patient_ids = [a[0] for a in assigned]
    if not patient_ids:
        return {"updated_count": 0, "critical_count": 0, "cursor": datetime.now(timezone.utc).isoformat()}

    recent_critical = db.query(PriorityAssessment).filter(
        PriorityAssessment.patient_id.in_(patient_ids),
        PriorityAssessment.priority_level == "P1_critical",
        PriorityAssessment.assessed_at >= since_dt
    ).count()

    total_updated = db.query(PriorityAssessment).filter(
        PriorityAssessment.patient_id.in_(patient_ids),
        PriorityAssessment.assessed_at >= since_dt
    ).count()

    return {
        "updated_count": total_updated,
        "critical_count": recent_critical,
        "cursor": datetime.now(timezone.utc).isoformat(),
    }


def get_patient_priority_breakdown(db: Session, patient_id: int) -> Dict[str, Any]:
    """Current priority tier with detailed breakdown of clinical and behavioral drivers."""
    pa = db.query(PriorityAssessment).filter(
        PriorityAssessment.patient_id == patient_id
    ).order_by(PriorityAssessment.assessed_at.desc()).first()

    if not pa:
        pa = calculate_patient_priority(db, patient_id)

    return {
        "patient_id": patient_id,
        "priority_level": pa.priority_level,
        "score": pa.score,
        "reasons": pa.reasons,
        "inputs": pa.inputs,
        "assessed_at": pa.assessed_at.isoformat() if pa.assessed_at else None,
    }


def get_priority_history(db: Session, patient_id: int) -> List[PriorityAssessment]:
    """Priority trajectory audit log."""
    return db.query(PriorityAssessment).filter(
        PriorityAssessment.patient_id == patient_id
    ).order_by(PriorityAssessment.assessed_at.desc()).all()


def get_priority_assessment_by_id(db: Session, assessment_id: int) -> Optional[PriorityAssessment]:
    """Get single assessment by ID."""
    return db.query(PriorityAssessment).filter(PriorityAssessment.id == assessment_id).first()


def get_all_priority_assessments(db: Session, skip: int = 0, limit: int = 100) -> List[PriorityAssessment]:
    """List priority assessments."""
    return db.query(PriorityAssessment).offset(skip).limit(limit).all()


def create_priority_assessment(db: Session, pa_in: Any) -> PriorityAssessment:
    """Explicitly create priority assessment."""
    patient_id = pa_in.patient_id
    return calculate_patient_priority(db, patient_id)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
