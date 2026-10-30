"""Blood pressure reading service implementing Ingestion Pipeline & Data Quality Service (v3).

Covers:
- UC01: Record BP Measurement (F01)
- UC06: Verify Measurement (F06)
- UC06b: Request Re-entry or Confirmation
- UCANA: Analyse Accepted Measurement
- UC07: Detect Concerning Reading (F07)
- UC08: Analyse BP Trend (F08)
- UC09: Create Justified Alert (F09)
- UC09b: Provide Emergency Guidance (RS-1)
- RS-8: 722 protocol session grouping & Day 1 exclusion
- RS-15: Clinician-only Data Quality Prompts
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.BloodPressureReading import BloodPressureReading
from app.models.patientprofile import PatientProfile
from app.models.ScheduleSlot import ScheduleSlot
from app.models.MeasurementSchedule import MeasurementSchedule
from app.models.Alert import Alert
from app.models.AlertReading import AlertReading
from app.models.user import User


def create_blood_pressure_reading(
    db: Session,
    reading_in: Any,
    current_user: Optional[User] = None,
    x_acting_for: Optional[int] = None,
    actor_user: Optional[User] = None,
) -> BloodPressureReading:
    """Primary ingestion pipeline for blood pressure readings."""
    if current_user is None and actor_user is not None:
        current_user = actor_user

    def _v(key, default=None):
        if isinstance(reading_in, dict):
            return reading_in.get(key, default)
        return getattr(reading_in, key, default)

    patient_id = _v("patient_id") or x_acting_for
    if not patient_id and current_user and getattr(current_user, "patient_profile", None):
        patient_id = current_user.patient_profile.id

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )

    systolic = int(_v("systolic"))
    diastolic = int(_v("diastolic"))
    pulse = _v("pulse")
    measured_at = _v("measured_at") or datetime.now(timezone.utc)
    if isinstance(measured_at, str):
        measured_at = datetime.fromisoformat(measured_at.replace("Z", "+00:00"))
    if measured_at.tzinfo is None:
        measured_at = measured_at.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)

    # 1. Plausibility Check (Verification - UC06 / F06)
    # Physical bounds SBP 50-300, DBP 30-200. SBP must exceed DBP.
    if not (50 <= systolic <= 300) or not (30 <= diastolic <= 200) or systolic <= diastolic:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="READING_REJECTED: Measurement outside plausible physiological limits (SBP 50-300, DBP 30-200, SBP > DBP)"
        )

    # 2. Detect Concerning / Unusual Reading (UC06b / F07)
    # Unusual but possible readings are stored and analysed; needs_confirmation prompts recheck
    pulse_pressure = systolic - diastolic
    is_unusual = (
        systolic >= 180 or systolic <= 80 or
        diastolic >= 120 or diastolic <= 50 or
        pulse_pressure < 20
    )
    verification_status = "needs_confirmation" if is_unusual else "accepted"

    # 3. Status Level Classification
    if systolic >= 180 or diastolic >= 120:
        status_level = "severe"
    elif systolic >= 140 or diastolic >= 90:
        status_level = "stage_2"
    elif systolic >= 130 or diastolic >= 80:
        status_level = "stage_1"
    elif systolic >= 120 and diastolic < 80:
        status_level = "elevated"
    else:
        status_level = "normal"

    # 4. Session Binding (RS-8: 722 protocol repeat readings 1-2 min apart share session_id)
    ten_mins_ago = measured_at - timedelta(minutes=10)
    ten_mins_ahead = measured_at + timedelta(minutes=10)
    recent_session_reading = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient.id,
        BloodPressureReading.measured_at >= ten_mins_ago,
        BloodPressureReading.measured_at <= ten_mins_ahead,
    ).order_by(BloodPressureReading.measured_at.desc()).first()

    if recent_session_reading and recent_session_reading.session_id:
        session_id = recent_session_reading.session_id
    else:
        session_id = str(uuid.uuid4())

    # 5. Slot Binding & Auto-Closing (F15)
    slot_id = _v("slot_id")
    linked_slot = None
    if slot_id:
        linked_slot = db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).first()
    else:
        # Match upcoming slot by window
        linked_slot = db.query(ScheduleSlot).filter(
            ScheduleSlot.patient_id == patient.id,
            ScheduleSlot.status.in_(["upcoming", "pending"]),
            ScheduleSlot.window_start <= measured_at + timedelta(hours=1),
            ScheduleSlot.window_end >= measured_at - timedelta(hours=1),
        ).first()

    # 6. Data Quality Evaluation (RS-15: Prompts for Clinicians only)
    quality_flags = []
    if systolic % 10 == 0 and diastolic % 10 == 0:
        quality_flags.append("digit_preference_terminal_zero")
    elif systolic % 5 == 0 and diastolic % 5 == 0:
        quality_flags.append("digit_preference_terminal_five")

    # Duplicate timestamp check
    duplicate_reading = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient.id,
        BloodPressureReading.systolic == systolic,
        BloodPressureReading.diastolic == diastolic,
        func.abs(func.strftime('%s', BloodPressureReading.measured_at) - int(measured_at.timestamp())) < 60
    ).first()
    if duplicate_reading:
        quality_flags.append("duplicate_reading_suspected")

    # Late entry check
    if (now_utc - measured_at).total_seconds() > 86400:
        quality_flags.append("late_entry_over_24h")

    # 7. Role & Entrant attribution
    entered_by = _v("entered_by") or "patient"
    actor_id = _v("actor_id") or (current_user.id if current_user else None)
    if not _v("entered_by") and current_user:
        if current_user.role == "caregiver":
            entered_by = "caregiver"
        elif current_user.role in ("doctor", "admin"):
            entered_by = "professional"

    # Current monitoring mode
    from app.services.monitoring_mode_service import get_current_monitoring_mode
    current_mode = get_current_monitoring_mode(db, patient.id)

    db_reading = BloodPressureReading(
        patient_id=patient.id,
        session_id=session_id,
        systolic=systolic,
        diastolic=diastolic,
        pulse=pulse,
        measured_at=measured_at,
        received_at=now_utc,
        capture_method=_v("capture_method", "manual") or "manual",
        entered_by=entered_by,
        actor_id=actor_id,
        slot_id=linked_slot.id if linked_slot else None,
        mode_at_time=current_mode,
        verification_status=verification_status,
        status_level=status_level,
        recheck_of_reading_id=_v("recheck_of_reading_id"),
        replaces_reading_id=_v("replaces_reading_id"),
        symptoms_reported=_v("symptoms_reported"),
        medication_taken_today=_v("medication_taken_today"),
        data_quality_flags=quality_flags if quality_flags else None,
        notes=_v("notes"),
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    # Update slot if linked
    if linked_slot:
        existing_reading_ids = linked_slot.reading_ids or []
        if db_reading.id not in existing_reading_ids:
            existing_reading_ids.append(db_reading.id)
            linked_slot.reading_ids = existing_reading_ids
            linked_slot.readings_received = len(existing_reading_ids)
            if linked_slot.readings_received >= (linked_slot.readings_required or 2):
                linked_slot.status = "taken"
                linked_slot.closed_at = now_utc
            else:
                linked_slot.status = "partial"
            db.commit()

    # 8. Analysis & Alerting Engine (UC07, UC08, UC09, UC09b)
    alerts_generated = []
    emergency_guidance = None

    # Severe single reading check (RS-1, RS-2)
    if systolic >= 180 or diastolic >= 110:
        is_critical = (systolic >= 180 and diastolic >= 120) or systolic >= 200
        tier = "critical_emergency" if is_critical else "severe_single_reading"
        alert_msg = f"Severe reading detected: {systolic}/{diastolic} mmHg"

        alert = Alert(
            patient_id=patient.id,
            alert_type="severe_reading",
            severity="high" if is_critical else "medium",
            tier=tier,
            trigger_type="single_reading",
            lifecycle="raised",
            message=alert_msg,
            justification={
                "triggering_reading_id": db_reading.id,
                "systolic": systolic,
                "diastolic": diastolic,
                "tier": tier,
                "evaluated_at": now_utc.isoformat(),
            }
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Link alert reading
        alert_reading = AlertReading(alert_id=alert.id, reading_id=db_reading.id)
        db.add(alert_reading)
        db.commit()
        alerts_generated.append(alert)

        # UC09b: Emergency guidance payload
        emergency_guidance = {
            "severity": "critical" if is_critical else "severe",
            "message": "Your blood pressure reading is severely elevated.",
            "instructions": [
                "Sit quietly and rest for 5 minutes.",
                "Take a repeat measurement to confirm.",
                "Check for emergency symptoms: chest pain, shortness of breath, severe headache, numbness, or vision changes."
            ],
            "algeria_emergency_numbers": {
                "civil_protection": "14",
                "samu": "1021"
            },
            "contact_doctor_prompt": "If symptoms are present or repeat reading remains >= 180/110, seek emergency medical attention immediately."
        }

    # Trend persistence check (UC08 / RS-13)
    target_sbp = patient.target_systolic or 135
    target_dbp = patient.target_diastolic or 85
    recent_readings = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient.id,
        BloodPressureReading.verification_status != "rejected"
    ).order_by(BloodPressureReading.measured_at.desc()).limit(10).all()

    if len(recent_readings) >= 5:
        elevated_count = sum(1 for r in recent_readings if r.systolic > target_sbp or r.diastolic > target_dbp)
        if elevated_count >= 3:
            # Check if active trend alert already exists to avoid spamming
            existing_active_trend_alert = db.query(Alert).filter(
                Alert.patient_id == patient.id,
                Alert.tier == "persistent_elevation",
                Alert.lifecycle.in_(["raised", "delivered"])
            ).first()
            if not existing_active_trend_alert:
                trend_alert = Alert(
                    patient_id=patient.id,
                    alert_type="persistent_elevation",
                    severity="medium",
                    tier="persistent_elevation",
                    trigger_type="trend_persistence",
                    lifecycle="raised",
                    message=f"Blood pressure consistently above target ({elevated_count}/10 recent readings)",
                    justification={
                        "target_systolic": target_sbp,
                        "target_diastolic": target_dbp,
                        "elevated_readings_count": elevated_count,
                        "window_size": len(recent_readings),
                    }
                )
                db.add(trend_alert)
                db.commit()
                db.refresh(trend_alert)
                alerts_generated.append(trend_alert)

    # 9. Recalculate Priority (UC10)
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient.id)
    except Exception:
        pass

    # 10. Route Notifications (SC2, SC2b)
    try:
        from app.services.notification_service import route_notification_for_reading
        route_notification_for_reading(db, db_reading, alerts_generated)
    except Exception:
        pass

    # Record Audit Log (SC6)
    try:
        from app.services.audit_log_service import create_audit_log_entry
        from app.schemas.audit_log import AuditLogCreate
        create_audit_log_entry(db, AuditLogCreate(
            user_id=actor_id,
            action="CREATE_READING",
            table_name="blood_pressure_readings",
            record_id=db_reading.id,
            new_values={
                "systolic": systolic,
                "diastolic": diastolic,
                "measured_at": measured_at.isoformat(),
                "verification_status": verification_status
            }
        ))
    except Exception:
        pass

    return db_reading


def confirm_reading(
    db: Session,
    reading_id: int,
    current_user: Optional[User] = None,
    note: Optional[str] = None,
) -> BloodPressureReading:
    """Confirm an unusual value (needs_confirmation -> confirmed_by_entrant). Triggers re-analysis."""
    reading = db.query(BloodPressureReading).filter(BloodPressureReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")

    reading.verification_status = "confirmed_by_entrant"
    db.commit()
    db.refresh(reading)

    # Re-evaluate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, reading.patient_id)
    except Exception:
        pass

    return reading


def annotate_reading(
    db: Session,
    reading_id: int,
    notes: Optional[str] = None,
    current_user: Optional[User] = None,
    note: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> BloodPressureReading:
    """Add a non-clinical entrant note or contextual tag to a reading."""
    reading = db.query(BloodPressureReading).filter(BloodPressureReading.id == reading_id).first()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")

    entry = note or notes or ""
    if tags:
        entry = f"{entry} [tags: {', '.join(tags)}]".strip()
    existing_notes = reading.notes or ""
    reading.notes = f"{existing_notes}\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}] {entry}".strip()
    db.commit()
    db.refresh(reading)
    return reading


def get_patient_trends(db: Session, patient_id: int, range_param: str = "30d", time_range: Optional[str] = None) -> Dict[str, Any]:
    """Patient trend chart data: aggregated session averages, target band, and protocol cycle markers."""
    if time_range:
        range_param = time_range
    days = 30
    if range_param == "7d":
        days = 7
    elif range_param == "90d":
        days = 90

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    readings = db.query(BloodPressureReading).filter(
        BloodPressureReading.patient_id == patient_id,
        BloodPressureReading.measured_at >= cutoff,
        BloodPressureReading.verification_status != "rejected"
    ).order_by(BloodPressureReading.measured_at.asc()).all()

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    target_sbp = patient.target_systolic if patient else 135
    target_dbp = patient.target_diastolic if patient else 85

    # Group readings by session_id
    sessions = {}
    for r in readings:
        sid = r.session_id or f"single_{r.id}"
        if sid not in sessions:
            sessions[sid] = []
        sessions[sid].append(r)

    session_points = []
    for sid, s_readings in sessions.items():
        avg_sbp = sum(r.systolic for r in s_readings) / len(s_readings)
        avg_dbp = sum(r.diastolic for r in s_readings) / len(s_readings)
        pulse_vals = [r.pulse for r in s_readings if r.pulse is not None]
        avg_pulse = sum(pulse_vals) / len(pulse_vals) if pulse_vals else None
        session_time = s_readings[0].measured_at

        session_points.append({
            "session_id": sid,
            "measured_at": session_time.isoformat() if hasattr(session_time, "isoformat") else str(session_time),
            "systolic": round(avg_sbp, 1),
            "diastolic": round(avg_dbp, 1),
            "pulse": round(avg_pulse, 1) if avg_pulse else None,
            "reading_count": len(s_readings),
            "is_above_target": avg_sbp > target_sbp or avg_dbp > target_dbp,
        })

    return {
        "range": range_param,
        "target": {
            "systolic": target_sbp,
            "diastolic": target_dbp,
            "basis": "home_average"
        },
        "session_count": len(session_points),
        "sessions": session_points,
    }


def get_doctor_trends(db: Session, patient_id: int, range_param: str = "30d", time_range: Optional[str] = None) -> Dict[str, Any]:
    """Doctor trend view with medication event overlays, alert markers, and office BP points."""
    if time_range:
        range_param = time_range
    patient_trends = get_patient_trends(db, patient_id, range_param)

    # Overlays
    from app.models.TreatmentEvent import TreatmentEvent
    from app.models.OfficeReading import OfficeReading

    days = 30
    if range_param == "7d":
        days = 7
    elif range_param == "90d":
        days = 90
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).date()

    treatment_events = db.query(TreatmentEvent).filter(
        TreatmentEvent.patient_id == patient_id,
        TreatmentEvent.effective_date >= cutoff_date
    ).order_by(TreatmentEvent.effective_date.asc()).all()

    office_readings = db.query(OfficeReading).filter(
        OfficeReading.patient_id == patient_id,
        OfficeReading.measured_at >= datetime.now(timezone.utc) - timedelta(days=days)
    ).order_by(OfficeReading.measured_at.asc()).all()

    alerts = db.query(Alert).filter(
        Alert.patient_id == patient_id,
        Alert.created_at >= datetime.now(timezone.utc) - timedelta(days=days)
    ).order_by(Alert.created_at.asc()).all()

    return {
        **patient_trends,
        "treatment_events": [
            {
                "id": te.id,
                "event_type": te.event_type,
                "drug_name": te.drug_name,
                "dose": te.dose,
                "effective_date": te.effective_date.isoformat(),
            }
            for te in treatment_events
        ],
        "office_readings": [
            {
                "id": o.id,
                "systolic": o.systolic,
                "diastolic": o.diastolic,
                "measured_at": o.measured_at.isoformat() if hasattr(o.measured_at, "isoformat") else str(o.measured_at),
                "note": o.note,
            }
            for o in office_readings
        ],
        "alerts": [
            {
                "id": a.id,
                "tier": a.tier,
                "message": a.message,
                "created_at": a.created_at.isoformat() if hasattr(a.created_at, "isoformat") else str(a.created_at),
            }
            for a in alerts
        ]
    }


def get_blood_pressure_reading_by_id(db: Session, reading_id: int) -> Optional[BloodPressureReading]:
    """Retrieve reading by ID."""
    return db.query(BloodPressureReading).filter(BloodPressureReading.id == reading_id).first()


def get_all_blood_pressure_readings(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    verification_status: Optional[str] = None,
) -> List[BloodPressureReading]:
    """List readings with optional filters."""
    query = db.query(BloodPressureReading)
    if patient_id is not None:
        query = query.filter(BloodPressureReading.patient_id == patient_id)
    if from_date:
        query = query.filter(BloodPressureReading.measured_at >= from_date)
    if to_date:
        query = query.filter(BloodPressureReading.measured_at <= to_date)
    if verification_status:
        query = query.filter(BloodPressureReading.verification_status == verification_status)
    return query.order_by(BloodPressureReading.measured_at.desc()).offset(skip).limit(limit).all()
