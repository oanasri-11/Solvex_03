"""ReminderPreference service (Section 10)."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.ReminderPreference import ReminderPreference
from app.models.patientprofile import PatientProfile
from app.models.ScheduleSlot import ScheduleSlot
from app.models.MeasurementSchedule import MeasurementSchedule


def get_reminder_preferences(db: Session, patient_id: int) -> Optional[ReminderPreference]:
    """Get reminder settings for a patient. Creates default if none exist."""
    prefs = db.query(ReminderPreference).filter(ReminderPreference.patient_id == patient_id).first()
    if not prefs:
        prefs = ReminderPreference(
            patient_id=patient_id,
            enabled=True,
            channel="push",
            lead_minutes=15,
            morning_time="08:00",
            evening_time="20:00",
            routine_day="sunday",
            routine_time="09:00",
            adaptive_missed_reminder=True,
            push_tokens=[],
        )
        try:
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        except SQLAlchemyError:
            db.rollback()
            return None
    return prefs


def replace_reminder_preferences(
    db: Session,
    patient_id: int,
    prefs_in: Any,
) -> Optional[ReminderPreference]:
    """Replace reminder settings (PUT /patients/me/reminder-preferences)."""
    try:
        prefs = db.query(ReminderPreference).filter(ReminderPreference.patient_id == patient_id).first()
        if not prefs:
            prefs = ReminderPreference(patient_id=patient_id)
            db.add(prefs)

        update_data = prefs_in.model_dump(exclude_unset=True) if hasattr(prefs_in, "model_dump") else dict(prefs_in)
        for k, v in update_data.items():
            if hasattr(prefs, k):
                setattr(prefs, k, v)

        db.commit()
        db.refresh(prefs)
        return prefs
    except SQLAlchemyError:
        db.rollback()
        raise


def get_upcoming_reminders(db: Session, patient_id: int) -> List[Dict[str, Any]]:
    """Get upcoming measurement reminders linked to slots."""
    now = datetime.now(timezone.utc)
    slots = (
        db.query(ScheduleSlot)
        .filter(
            ScheduleSlot.patient_id == patient_id,
            ScheduleSlot.window_end >= now,
            ScheduleSlot.status.in_(["upcoming", "open"]),
        )
        .order_by(ScheduleSlot.due_at.asc())
        .limit(10)
        .all()
    )

    prefs = get_reminder_preferences(db, patient_id)
    lead = prefs.lead_minutes if prefs else 15
    channel = prefs.channel if prefs else "push"

    reminders = []
    for slot in slots:
        reminders.append({
            "slot_id": slot.id,
            "due_at": slot.due_at,
            "window_start": slot.window_start,
            "window_end": slot.window_end,
            "lead_minutes": lead,
            "channel": channel,
            "message": "Time for your blood pressure measurement.",
        })
    return reminders


def register_push_token(
    db: Session,
    patient_id: int,
    token: str,
    device_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Register or refresh a push notification token."""
    prefs = get_reminder_preferences(db, patient_id)
    if not prefs:
        raise ValueError("Patient reminder preferences not found")

    tokens = list(prefs.push_tokens or [])
    # Update existing or add new
    existing = False
    for item in tokens:
        if isinstance(item, dict) and item.get("token") == token:
            item["updated_at"] = datetime.now(timezone.utc).isoformat()
            if device_name:
                item["device_name"] = device_name
            existing = True
            break

    if not existing:
        tokens.append({
            "token": token,
            "device_name": device_name or "Mobile App",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    prefs.push_tokens = tokens
    try:
        db.commit()
        db.refresh(prefs)
        return {"status": "registered", "token": token}
    except SQLAlchemyError:
        db.rollback()
        raise


def remove_push_token(
    db: Session,
    patient_id: int,
    token_id_or_val: str,
) -> bool:
    """Remove a push notification token."""
    prefs = db.query(ReminderPreference).filter(ReminderPreference.patient_id == patient_id).first()
    if not prefs or not prefs.push_tokens:
        return True

    tokens = [
        t for t in (prefs.push_tokens or [])
        if (isinstance(t, dict) and t.get("token") != token_id_or_val and str(t.get("id", "")) != token_id_or_val)
    ]
    prefs.push_tokens = tokens
    try:
        db.commit()
        db.refresh(prefs)
        return True
    except SQLAlchemyError:
        db.rollback()
        raise
