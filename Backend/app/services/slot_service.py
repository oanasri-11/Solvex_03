<<<<<<< HEAD


from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ScheduleSlot import ScheduleSlot
from app.models.MeasurementSchedule import MeasurementSchedule
from app.schemas.schedule_slot import (
    ScheduleSlotCreate,
    ScheduleSlotUpdate,
    ScheduleSlotOut,
)


def create_schedule_slot(db: Session, slot_in: ScheduleSlotCreate) -> Optional[ScheduleSlot]:
    """Create a schedule slot (system-generated). Verifies the schedule exists."""
    try:
        schedule = (
            db.query(MeasurementSchedule)
            .filter(MeasurementSchedule.id == slot_in.schedule_id)
            .first()
        )
        if not schedule:
            return None
        scheduled_at = getattr(slot_in, "scheduled_at", None) or datetime.utcnow()
        status = getattr(slot_in, "status", None) or "pending"
        db_slot = ScheduleSlot(
            schedule_id=slot_in.schedule_id,
            scheduled_at=scheduled_at,
            status=status,
            reading_id=getattr(slot_in, "reading_id", None),
            completed_at=getattr(slot_in, "completed_at", None),
        )
        db.add(db_slot)
        db.commit()
        db.refresh(db_slot)
        return db_slot
    except SQLAlchemyError:
        db.rollback()
        raise


def get_schedule_slot_by_id(db: Session, slot_id: int) -> Optional[ScheduleSlot]:
    """Retrieve a slot by its primary key."""
    return db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).first()


def get_all_schedule_slots(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    schedule_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """List slots with optional schedule_id / status filters."""
    query = db.query(ScheduleSlot)
    if schedule_id is not None:
        query = query.filter(ScheduleSlot.schedule_id == schedule_id)
    if status is not None:
        query = query.filter(ScheduleSlot.status == status)
    return query.offset(skip).limit(limit).all()


def update_schedule_slot(
    db: Session, slot_id: int, slot_in: ScheduleSlotUpdate
) -> Optional[ScheduleSlot]:
    """Update a slot (used to confirm/close a slot). Fails if already closed."""
    try:
        db_slot = get_schedule_slot_by_id(db, slot_id)
        if not db_slot:
            return None
        if db_slot.status in ("completed", "taken", "not_taken", "missed"):
            # A slot cannot be confirmed twice.
            return None
        update_data = slot_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_slot, field, value)
        if db_slot.status in ("completed", "taken") and db_slot.completed_at is None:
            db_slot.completed_at = datetime.utcnow()# type: ignore
        db.add(db_slot)
        db.commit()
        db.refresh(db_slot)
        return db_slot
    except SQLAlchemyError:
        db.rollback()
        raise


=======
"""ScheduleSlot service (Section 9, UC15, F15, SC1, RS-3)."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ScheduleSlot import ScheduleSlot
from app.models.patientprofile import PatientProfile
from app.models.BloodPressureReading import BloodPressureReading
from app.models.Alert import Alert


def confirm_slot(
    db: Session,
    slot_id: int,
    taken: bool = True,
    reading_ids: Optional[List[int]] = None,
    reason: Optional[str] = None,
    actor_id: Optional[int] = None,
) -> ScheduleSlot:
    """Close a slot (F15): with readings or as not taken with optional reason (NSLOT)."""
    slot = db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")

    if slot.status in ["taken", "not_taken"] and slot.closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SLOT_ALREADY_CLOSED: Slot is already closed"
        )

    now = datetime.now(timezone.utc)
    if taken:
        slot.status = "taken"
        if reading_ids:
            slot.reading_ids = reading_ids
            slot.readings_received = len(reading_ids)
    else:
        slot.status = "not_taken"
        slot.reason = reason

    slot.closed_at = now
    db.commit()
    db.refresh(slot)

    # Recalculate priority
    if slot.patient_id:
        try:
            from app.services.priority_service import calculate_patient_priority
            calculate_patient_priority(db, slot.patient_id)
        except Exception:
            pass

    return slot


def doctor_confirm_slot(
    db: Session,
    slot_id: int,
    doctor_id: Optional[int] = None,
    taken: bool = True,
    reading_ids: Optional[List[int]] = None,
    reason: Optional[str] = None,
    doctor_user_id: Optional[int] = None,
    patient_id: Optional[int] = None,
) -> ScheduleSlot:
    """Doctor-assisted slot confirmation."""
    actor_id = doctor_id or doctor_user_id or 1
    return confirm_slot(db, slot_id, taken=taken, reading_ids=reading_ids, reason=reason, actor_id=actor_id)


def evaluate_schedule_and_detect_missed(db: Session, patient_id: Optional[int] = None) -> List[ScheduleSlot]:
    """Automated evaluation (SC1): transitions expired open slots to missed or partial."""
    now = datetime.now(timezone.utc)
    query = db.query(ScheduleSlot).filter(
        ScheduleSlot.status.in_(["upcoming", "pending"]),
        ScheduleSlot.window_end < now
    )
    if patient_id:
        query = query.filter(ScheduleSlot.patient_id == patient_id)

    expired_slots = query.all()
    updated = []
    patients_affected = set()

    for s in expired_slots:
        if s.readings_received and s.readings_received > 0:
            s.status = "partial"
        else:
            s.status = "missed"
        s.closed_at = now
        updated.append(s)
        if s.patient_id:
            patients_affected.add(s.patient_id)

    db.commit()

    # Recalculate priority for affected patients
    for pid in patients_affected:
        try:
            from app.services.priority_service import calculate_patient_priority
            calculate_patient_priority(db, pid)
        except Exception:
            pass

    return updated


def calculate_adherence(
    db: Session,
    patient_id: int,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Calculate adherence metrics (RS-3)."""
    query = db.query(ScheduleSlot).filter(ScheduleSlot.patient_id == patient_id)
    if from_date:
        query = query.filter(ScheduleSlot.due_at >= from_date)
    if to_date:
        query = query.filter(ScheduleSlot.due_at <= to_date)

    slots = query.all()
    total_slots = len(slots)
    if total_slots == 0:
        return {
            "total_slots": 0,
            "taken_slots": 0,
            "missed_slots": 0,
            "partial_slots": 0,
            "not_taken_slots": 0,
            "adherence_rate": 1.0,
            "rating": "no_data",
        }

    taken = sum(1 for s in slots if s.status == "taken")
    missed = sum(1 for s in slots if s.status == "missed")
    partial = sum(1 for s in slots if s.status == "partial")
    not_taken = sum(1 for s in slots if s.status == "not_taken")

    adherence_rate = round(taken / total_slots, 2)
    if adherence_rate >= 0.8:
        rating = "good"
    elif adherence_rate >= 0.6:
        rating = "suboptimal"
    else:
        rating = "poor"

    return {
        "total_slots": total_slots,
        "taken_slots": taken,
        "missed_slots": missed,
        "partial_slots": partial,
        "not_taken_slots": not_taken,
        "adherence_rate": adherence_rate,
        "rating": rating,
    }


def get_schedule_slots(
    db: Session,
    patient_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    status_filter: Optional[str] = None,
    status: Optional[str] = None,
) -> List[ScheduleSlot]:
    status_filter = status or status_filter
    """Query schedule slots."""
    query = db.query(ScheduleSlot)
    if patient_id is not None:
        query = query.filter(ScheduleSlot.patient_id == patient_id)
    if from_date:
        query = query.filter(ScheduleSlot.due_at >= from_date)
    if to_date:
        query = query.filter(ScheduleSlot.due_at <= to_date)
    if status_filter:
        query = query.filter(ScheduleSlot.status == status_filter)
    return query.order_by(ScheduleSlot.due_at.asc()).all()


def get_schedule_slot_by_id(db: Session, slot_id: int) -> Optional[ScheduleSlot]:
    """Retrieve slot by ID."""
    return db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).first()


def create_schedule_slot(db: Session, slot_data: Any) -> ScheduleSlot:
    """Create a schedule slot."""
    slot = ScheduleSlot(
        schedule_id=slot_data.schedule_id,
        scheduled_at=getattr(slot_data, "scheduled_at", None) or getattr(slot_data, "due_at", datetime.now(timezone.utc)),
        due_at=getattr(slot_data, "due_at", None) or getattr(slot_data, "scheduled_at", datetime.now(timezone.utc)),
        status=getattr(slot_data, "status", "upcoming"),
        reading_id=getattr(slot_data, "reading_id", None),
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def update_schedule_slot(db: Session, slot_id: int, slot_update: Any) -> Optional[ScheduleSlot]:
    """Update a schedule slot."""
    slot = get_schedule_slot_by_id(db, slot_id)
    if not slot:
        return None
    for field, val in slot_update.dict(exclude_unset=True).items():
        setattr(slot, field, val)
    db.commit()
    db.refresh(slot)
    return slot


def get_all_schedule_slots(db: Session, skip: int = 0, limit: int = 100) -> List[ScheduleSlot]:
    """List all schedule slots."""
    return db.query(ScheduleSlot).offset(skip).limit(limit).all()
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
