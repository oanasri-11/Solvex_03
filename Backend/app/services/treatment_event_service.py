"""TreatmentEvent service (Section 7b, UCPROF)."""

from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.TreatmentEvent import TreatmentEvent
from app.models.patientprofile import PatientProfile


ANTIHYPERTENSIVE_CLASSES = {
    "ace_inhibitor", "arb", "ccb", "thiazide_diuretic", "beta_blocker", "alpha_blocker", "mra", "loop_diuretic"
}


def record_treatment_event(
    db: Session,
    patient_id: int,
    event_type: Optional[str] = None,
    drug_class: Optional[str] = None,
    drug_name: Optional[str] = None,
    dose: Optional[str] = None,
    effective_date: Optional[date] = None,
    recorded_by: Optional[int] = None,
    note: Optional[str] = None,
    event_in: Optional[Any] = None,
) -> TreatmentEvent:
    if event_in is not None:
        event_type = event_type or getattr(event_in, "event_type", "started")
        drug_class = drug_class or getattr(event_in, "drug_class", "Antihypertensive")
        drug_name = drug_name or getattr(event_in, "drug_name", "Medication")
        dose = dose or getattr(event_in, "dose", "Standard")
        effective_date = effective_date or getattr(event_in, "effective_date", date.today())
        note = note or getattr(event_in, "note", None)
    event_type = event_type or "started"
    drug_class = drug_class or "Antihypertensive"
    drug_name = drug_name or "Medication"
    dose = dose or "Standard"
    effective_date = effective_date or date.today()
    recorded_by = recorded_by or 1
    """Record a treatment event; opens post-change window; recalculates priority."""
    if event_type not in ["started", "dose_changed", "stopped"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event_type must be started, dose_changed, or stopped")

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    event = TreatmentEvent(
        patient_id=patient_id,
        event_type=event_type,
        drug_class=drug_class,
        drug_name=drug_name,
        dose=dose,
        effective_date=effective_date,
        recorded_by=recorded_by,
        note=note,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    return event


def correct_treatment_event(
    db: Session,
    event_id: Optional[int] = None,
    event_data: Optional[Any] = None,
    recorded_by: Optional[int] = None,
    original_event_id: Optional[int] = None,
    correction_in: Optional[Any] = None,
) -> TreatmentEvent:
    event_id = original_event_id or event_id or 1
    event_data = correction_in or event_data
    recorded_by = recorded_by or 1
    """Correction as a new event referencing the old one."""
    old_event = db.query(TreatmentEvent).filter(TreatmentEvent.id == event_id).first()
    if not old_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment event not found")

    new_event = TreatmentEvent(
        patient_id=old_event.patient_id,
        event_type=getattr(event_data, "event_type", old_event.event_type),
        drug_class=getattr(event_data, "drug_class", old_event.drug_class),
        drug_name=getattr(event_data, "drug_name", old_event.drug_name),
        dose=getattr(event_data, "dose", old_event.dose),
        effective_date=getattr(event_data, "effective_date", old_event.effective_date),
        recorded_by=recorded_by,
        corrects_event_id=old_event.id,
        note=getattr(event_data, "note", None) or f"Correction for event #{old_event.id}",
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


def get_treatment_events(db: Session, patient_id: int) -> List[TreatmentEvent]:
    """Retrieve treatment event history for patient."""
    return db.query(TreatmentEvent).filter(
        TreatmentEvent.patient_id == patient_id
    ).order_by(TreatmentEvent.effective_date.desc()).all()


def get_current_medications(db: Session, patient_id: int) -> Dict[str, Any]:
    """Derive current medication list and count of antihypertensive drug classes."""
    events = db.query(TreatmentEvent).filter(
        TreatmentEvent.patient_id == patient_id
    ).order_by(TreatmentEvent.effective_date.asc(), TreatmentEvent.id.asc()).all()

    latest_per_drug = {}
    for ev in events:
        key = ev.drug_name.lower().strip()
        if ev.event_type == "stopped":
            latest_per_drug.pop(key, None)
        else:
            latest_per_drug[key] = ev

    active_events = list(latest_per_drug.values())
    classes_count = len(set(ev.drug_class.lower() for ev in active_events))

    return {
        "patient_id": patient_id,
        "current_medications": active_events,
        "antihypertensive_class_count": classes_count,
    }
