"""Build a minimized, structured clinical context for the AI summarizer.

The context is intentionally JSON-serializable and excludes personally
identifiable information (phone, address, emergency contact, email).  Only the
patient's clinical monitoring profile and records are passed to the LLM.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.Alert import Alert
from app.models.ScheduleSlot import ScheduleSlot
from app.services.case_review_service import get_all_case_reviews
from app.services.condition_service import get_all_patient_conditions
from app.services.follow_up_action_service import get_all_follow_up_actions
from app.services.monitoring_mode_service import get_monitoring_mode_by_patient
from app.services.patient_service import get_patient_profile_by_id
from app.services.priority_service import get_all_priority_assessments
from app.services.reading_service import get_all_blood_pressure_readings
from app.services.schedule_service import get_active_schedule_for_patient

MIN_PERIOD_DAYS = 1
MAX_PERIOD_DAYS = 365
MAX_READINGS_IN_CONTEXT = 100


def _to_iso(value: Any) -> Optional[str]:
    """Serialise a datetime to a timezone-aware ISO-8601 string."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _age_band(age: int) -> str:
    if age < 18:
        return "under_18"
    if age < 40:
        return "18-39"
    if age < 60:
        return "40-59"
    if age < 80:
        return "60-79"
    return "80-plus"


def _build_blood_pressure(readings: List[Any], period_days: int) -> Dict[str, Any]:
    window_start = datetime.now(timezone.utc) - timedelta(days=period_days)
    payload: Dict[str, Any] = {
        "measurement_window_start": _to_iso(window_start),
        "measurement_window_end": _to_iso(datetime.now(timezone.utc)),
        "reading_count": len(readings),
        "pulse_available": False,
        "symptoms_available": False,
        "notes_source": True,
        "readings": [],
    }
    for reading in readings:
        payload["readings"].append(
            {
                "systolic": reading.systolic,
                "diastolic": reading.diastolic,
                "measured_at": _to_iso(reading.measured_at),
                "notes": reading.notes,
                "created_at": _to_iso(reading.created_at),
            }
        )
    return payload


def _build_trends(readings: List[Any]) -> Dict[str, Any]:
    if not readings:
        return {
            "readings_count": 0,
            "newest_systolic": None,
            "newest_diastolic": None,
            "oldest_systolic": None,
            "oldest_diastolic": None,
            "delta_systolic": None,
            "delta_diastolic": None,
            "direction": "insufficient_data",
            "trend_analysis_results": [],
            "note": "No readings were available in the requested window, so no trend could be computed.",
        }
    newest = readings[-1]
    oldest = readings[0]
    delta_systolic = newest.systolic - oldest.systolic
    delta_diastolic = newest.diastolic - oldest.diastolic
    if delta_systolic > 0 and delta_systolic >= abs(delta_diastolic):
        direction = "rising"
    elif delta_systolic < 0 and abs(delta_systolic) >= abs(delta_diastolic):
        direction = "falling"
    elif delta_diastolic > 0:
        direction = "rising"
    elif delta_diastolic < 0:
        direction = "falling"
    else:
        direction = "stable"
    return {
        "readings_count": len(readings),
        "newest_systolic": newest.systolic,
        "newest_diastolic": newest.diastolic,
        "oldest_systolic": oldest.systolic,
        "oldest_diastolic": oldest.diastolic,
        "delta_systolic": delta_systolic,
        "delta_diastolic": delta_diastolic,
        "direction": direction,
        "trend_analysis_results": [],
        "note": "Direction is derived from the difference between the newest and oldest reading in the window. It is descriptive only; no clinical thresholds or the rule engine were applied.",
    }
def _build_alerts(db: Session, patient_id: int) -> Dict[str, Any]:
    alerts = (
        db.query(Alert)
        .filter(Alert.patient_id == patient_id)
        .order_by(Alert.created_at.desc())
        .all()
    )
    open_alerts: List[Dict[str, Any]] = []
    for alert in alerts:
        if alert.status in {"new", "open", "raised", "delivered", "acknowledged"}:
            open_alerts.append(
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "status": alert.status,
                    "message": alert.message,
                    "created_at": _to_iso(alert.created_at),
                    "acknowledged_at": _to_iso(alert.acknowledged_at),
                    "resolved_at": _to_iso(alert.resolved_at),
                }
            )
    return {
        "open_alerts": open_alerts,
        "all_alert_count": len(alerts),
        "open_alert_count": len(open_alerts),
        "alert_types": sorted({a.alert_type for a in alerts}),
        "justification_available": False,
        "note": "The Alert model has no dedicated justification field; the `message` field (when set) is included for context.",
    }


def _build_adherence(db: Session, patient_id: int) -> Dict[str, Any]:# type: ignore
    schedule = get_active_schedule_for_patient(db, patient_id)
    if schedule is not None:
        schedule_payload: Dict[str, Any] = {
            "id": schedule.id,
            "frequency": schedule.frequency,
            "time_of_day": schedule.time_of_day,
            "days_of_week": list(schedule.days_of_week) if schedule.days_of_week else None,# type: ignore
            "is_active": schedule.is_active,
        }
        slots = (
            db.query(ScheduleSlot)
            .filter(ScheduleSlot.schedule_id == schedule.id)
            .order_by(ScheduleSlot.scheduled_at.asc())
            .all()
        )
    else:
        schedule_payload = None# type: ignore
        slots = []
    completed = [s for s in slots if s.status == "completed"]# type: ignore
    missed = [s for s in slots if s.status == "missed"]# type: ignore
    pending = [s for s in slots if s.status == "pending"]# type: ignore
    return {
        "active_schedule_id": schedule.id if schedule else None,
        "schedule": schedule_payload,
        "slot_count": len(slots),
        "completed_count": len(completed),
        "missed_count": len(missed),
        "pending_count": len(pending),
        "slots": [
            {
                "id": slot.id,
                "scheduled_at": _to_iso(slot.scheduled_at),
                "status": slot.status,
                "reading_id": slot.reading_id,
                "completed_at": _to_iso(slot.completed_at),
            }
            for slot in slots
        ],
    }
def _build_previous_followup(db: Session, patient_id: int) -> Dict[str, Any]:
    case_reviews = get_all_case_reviews(db, patient_id=patient_id)
    follow_up_actions = get_all_follow_up_actions(db, patient_id=patient_id)
    priority_assessments = get_all_priority_assessments(db, patient_id=patient_id)

    return {
        "case_reviews": [
            {
                "id": review.id,
                "status": review.status,
                "reviewed_at": _to_iso(review.reviewed_at),
                "summary": review.summary,
            }
            for review in case_reviews
        ],
        "follow_up_actions": [
            {
                "id": action.id,
                "type": action.type,
                "status": action.status,
                "due_date": _to_iso(action.due_date),
                "completed_at": _to_iso(action.completed_at),
                "notes": action.notes,
            }
            for action in follow_up_actions
        ],
        "priority_assessments": [
            {
                "id": assessment.id,
                "level": assessment.level,
                "assessed_at": _to_iso(assessment.assessed_at),
                "notes": assessment.notes,
            }
            for assessment in priority_assessments
        ],
        "pending_actions_count": sum(
            1 for action in follow_up_actions if action.status == "pending"# type: ignore
        ),
        "completed_actions_count": sum(
            1 for action in follow_up_actions if action.status == "completed"# type: ignore
        ),
    }


def build_patient_context(db: Session, patient_id: int, period_days: int = 30) -> Dict[str, Any]:
    period_days = max(MIN_PERIOD_DAYS, min(MAX_PERIOD_DAYS, int(period_days)))

    patient = get_patient_profile_by_id(db, patient_id)
    if not patient:
        raise ValueError(f"Patient with id {patient_id} not found")

    since = datetime.now(timezone.utc) - timedelta(days=period_days)
    all_readings = get_all_blood_pressure_readings(
        db, patient_id=patient_id, limit=MAX_READINGS_IN_CONTEXT
    )
    readings = [
        reading
        for reading in all_readings
        if reading.measured_at is not None and (reading.measured_at.replace(tzinfo=None) if getattr(reading.measured_at, 'tzinfo', None) else reading.measured_at) >= since.replace(tzinfo=None)# type: ignore
    ]
    readings.sort(key=lambda reading: reading.measured_at or datetime.min)

    clinical_profile: Dict[str, Any] = {}
    dob = patient.date_of_birth
    if dob is not None:
        age_days = (datetime.now(timezone.utc).date() - dob.date()).days
        age = max(age_days // 365, 0)
        clinical_profile["age_year"] = age
        clinical_profile["age_band"] = _age_band(age)
    if patient.gender:# type: ignore
        clinical_profile["gender"] = patient.gender
    conditions = get_all_patient_conditions(db, patient_id=patient_id, is_active=True)
    clinical_profile["conditions"] = [condition.condition_name for condition in conditions]
    monitoring_mode = get_monitoring_mode_by_patient(db, patient_id)
    if monitoring_mode is not None:
        clinical_profile["monitoring_mode"] = monitoring_mode.mode
    clinical_profile["bp_targets"] = None
    clinical_profile["treatment_status"] = None

    blood_pressure = _build_blood_pressure(readings, period_days)
    trends = _build_trends(readings)
    alerts = _build_alerts(db, patient_id)
    adherence = _build_adherence(db, patient_id)
    previous_followup = _build_previous_followup(db, patient_id)

    data_limitations: List[str] = []
    if not readings:
        data_limitations.append("No blood pressure readings were found in the requested window.")
    if not clinical_profile.get("conditions"):
        data_limitations.append("No active clinical conditions were recorded for this patient.")
    if clinical_profile.get("bp_targets") is None:
        data_limitations.append(
            "BP targets are not captured as structured fields in the monitoring data model."
        )
    if clinical_profile.get("treatment_status") is None:
        data_limitations.append(
            "Treatment/medication status is not stored as a structured field in the monitoring data model."
        )
    if not clinical_profile.get("monitoring_mode"):
        data_limitations.append("Monitoring mode is not configured for this patient.")

    return {
        "patient_id": patient_id,
        "period_days": period_days,
        "generated_at": _to_iso(datetime.now(timezone.utc)),
        "clinical_profile": clinical_profile,
        "blood_pressure": blood_pressure,
        "trends": trends,
        "alerts": alerts,
        "adherence": adherence,
        "previous_followup": previous_followup,
        "data_limitations": data_limitations,
    }
