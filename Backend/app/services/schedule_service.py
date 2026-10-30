<<<<<<< HEAD


from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.MeasurementSchedule import MeasurementSchedule
from app.models.patientprofile import PatientProfile
from app.schemas.schedule import (
    MeasurementScheduleCreate,
    MeasurementScheduleUpdate,
    MeasurementScheduleOut,
)


def create_measurement_schedule(
    db: Session, schedule_in: MeasurementScheduleCreate
) -> Optional[MeasurementSchedule]:
    """Define a measurement schedule for a patient. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == schedule_in.patient_id).first()
        )
        if not patient:
            return None
        is_active = getattr(schedule_in, "is_active", True)
        if is_active is None:
            is_active = True
        db_schedule = MeasurementSchedule(
            patient_id=schedule_in.patient_id,
            frequency=schedule_in.frequency,
            time_of_day=getattr(schedule_in, "time_of_day", None),
            days_of_week=getattr(schedule_in, "days_of_week", None),
            is_active=is_active,
        )
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except SQLAlchemyError:
        db.rollback()
        raise


def get_measurement_schedule_by_id(db: Session, schedule_id: int) -> Optional[MeasurementSchedule]:
    """Retrieve a schedule by its primary key."""
    return (
        db.query(MeasurementSchedule).filter(MeasurementSchedule.id == schedule_id).first()
    )


def get_all_measurement_schedules(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    """List schedules with optional patient_id / is_active filters."""
    query = db.query(MeasurementSchedule)
    if patient_id is not None:
        query = query.filter(MeasurementSchedule.patient_id == patient_id)
    if is_active is not None:
        query = query.filter(MeasurementSchedule.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def get_active_schedule_for_patient(
    db: Session, patient_id: int
) -> Optional[MeasurementSchedule]:
    """Retrieve the active schedule for a patient (only one is expected to be active)."""
    return (
        db.query(MeasurementSchedule)
        .filter(MeasurementSchedule.patient_id == patient_id, MeasurementSchedule.is_active == True)  # noqa: E712
        .first()
    )


def update_measurement_schedule(
    db: Session, schedule_id: int, schedule_in: MeasurementScheduleUpdate
) -> Optional[MeasurementSchedule]:
    """Edit a schedule. Per spec, an edit creates a new version; this implementation
    updates the existing record because the model carries no version field."""
    try:
        db_schedule = get_measurement_schedule_by_id(db, schedule_id)
        if not db_schedule:
            return None
        update_data = schedule_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_schedule, field, value)
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except SQLAlchemyError:
        db.rollback()
        raise


def deactivate_measurement_schedule(db: Session, schedule_id: int) -> Optional[MeasurementSchedule]:
    """Deactivate a schedule (is_active = False). No hard delete."""
    try:
        db_schedule = get_measurement_schedule_by_id(db, schedule_id)
        if not db_schedule:
            return None
        db_schedule.is_active = False# type: ignore
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except SQLAlchemyError:
        db.rollback()
        raise
=======
"""MeasurementSchedule service (Section 8, UC16, F16, RS-8)."""

from datetime import datetime, date, timezone, timedelta, time
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.MeasurementSchedule import MeasurementSchedule
from app.models.ScheduleSlot import ScheduleSlot
from app.models.patientprofile import PatientProfile
from app.models.BloodPressureReading import BloodPressureReading


def get_recommended_protocols() -> List[Dict[str, Any]]:
    """Return recommended clinical protocols (RS-8: 722 protocol & maintenance)."""
    return [
        {
            "protocol": "722_diagnostic",
            "name": "722 Diagnostic Protocol",
            "description": "7 consecutive days, 2 morning readings and 2 evening readings (1 min gap). Day 1 discarded for baseline calculation.",
            "cycle_length_days": 7,
            "readings_per_slot": 2,
            "min_gap_seconds": 60,
            "windows": {
                "morning": {"start": "06:00", "end": "10:00"},
                "evening": {"start": "18:00", "end": "22:00"}
            },
            "minimum_valid_readings": 12,
            "minimum_days": 3,
        },
        {
            "protocol": "722_followup",
            "name": "722 Follow-up Protocol",
            "description": "Quarterly 7-day monitoring week prior to clinical review.",
            "cycle_length_days": 7,
            "readings_per_slot": 2,
            "min_gap_seconds": 60,
            "windows": {
                "morning": {"start": "06:00", "end": "10:00"},
                "evening": {"start": "18:00", "end": "22:00"}
            },
            "minimum_valid_readings": 12,
            "minimum_days": 3,
        },
        {
            "protocol": "maintenance",
            "name": "Maintenance Protocol",
            "description": "Weekly routine measurement (e.g. Sunday morning) for stable patients.",
            "cycle_length_days": 28,
            "readings_per_slot": 1,
            "min_gap_seconds": 60,
            "windows": {
                "morning": {"start": "07:00", "end": "11:00"}
            },
        }
    ]


def create_measurement_schedule(
    db: Session,
    patient_id: int,
    schedule_data: Any = None,
    creator_role: str = "doctor",
    creator_id: Optional[int] = None,
    schedule_in: Any = None,
    owner: Optional[str] = None,
    created_by: Optional[int] = None,
) -> MeasurementSchedule:
    """Create a new measurement schedule and generate future slots."""
    data = schedule_in if schedule_in is not None else schedule_data
    role = owner if owner is not None else creator_role
    cid = created_by if created_by is not None else creator_id
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    from app.services.monitoring_mode_service import get_current_monitoring_mode
    current_mode = get_current_monitoring_mode(db, patient_id)

    # Ownership check (Design note NMODE)
    # in telemonitoring, doctor defines or approves; patient creates in self-monitoring
    if current_mode == "telemonitoring" and role == "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SCHEDULE_OWNED_BY_DOCTOR: Schedules in telemonitoring must be defined or approved by your doctor"
        )

    # Deactivate existing active schedules
    existing_schedules = db.query(MeasurementSchedule).filter(
        MeasurementSchedule.patient_id == patient_id,
        MeasurementSchedule.is_active == True  # noqa: E712
    ).all()
    for s in existing_schedules:
        s.is_active = False

    protocol = getattr(data, "protocol", "722_followup") or "722_followup"
    cycle_days = getattr(data, "cycle_length_days", 7) or 7
    start_dt = getattr(data, "start_date", None) or date.today()
    end_dt = getattr(data, "end_date", None) or (start_dt + timedelta(days=cycle_days))

    windows = getattr(data, "windows", None) or {
        "morning": {"start": "06:00", "end": "10:00"},
        "evening": {"start": "18:00", "end": "22:00"}
    }

    db_schedule = MeasurementSchedule(
        patient_id=patient_id,
        owner="patient" if role == "patient" else "doctor",
        protocol=protocol,
        readings_per_slot=getattr(data, "readings_per_slot", 2) or 2,
        min_gap_seconds=getattr(data, "min_gap_seconds", 60) or 60,
        windows=windows,
        cycle_length_days=cycle_days,
        start_date=start_dt,
        end_date=end_dt,
        version=1,
        pending_approval=(role == "patient" and current_mode == "telemonitoring"),
        created_by=cid,
        approved_by=cid if role == "doctor" else None,
        is_active=True,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    # Generate slots for cycle
    generate_slots_for_schedule(db, db_schedule)

    return db_schedule


def generate_slots_for_schedule(db: Session, schedule: MeasurementSchedule) -> None:
    """Generate ScheduleSlot records for morning and evening windows across the cycle."""
    start = schedule.start_date or date.today()
    end = schedule.end_date or (start + timedelta(days=schedule.cycle_length_days or 7))
    cycle_id = f"cycle_{schedule.id}_{start.isoformat()}"

    curr = start
    while curr <= end:
        # Morning slot
        m_start = datetime.combine(curr, time(6, 0), tzinfo=timezone.utc)
        m_end = datetime.combine(curr, time(10, 0), tzinfo=timezone.utc)
        m_due = datetime.combine(curr, time(8, 0), tzinfo=timezone.utc)

        morning_slot = ScheduleSlot(
            schedule_id=schedule.id,
            cycle_id=cycle_id,
            patient_id=schedule.patient_id,
            scheduled_at=m_due,
            due_at=m_due,
            window_start=m_start,
            window_end=m_end,
            readings_required=schedule.readings_per_slot or 2,
            readings_received=0,
            reading_ids=[],
            status="upcoming",
        )
        db.add(morning_slot)

        # Evening slot
        e_start = datetime.combine(curr, time(18, 0), tzinfo=timezone.utc)
        e_end = datetime.combine(curr, time(22, 0), tzinfo=timezone.utc)
        e_due = datetime.combine(curr, time(20, 0), tzinfo=timezone.utc)

        evening_slot = ScheduleSlot(
            schedule_id=schedule.id,
            cycle_id=cycle_id,
            patient_id=schedule.patient_id,
            scheduled_at=e_due,
            due_at=e_due,
            window_start=e_start,
            window_end=e_end,
            readings_required=schedule.readings_per_slot or 2,
            readings_received=0,
            reading_ids=[],
            status="upcoming",
        )
        db.add(evening_slot)

        curr += timedelta(days=1)

    db.commit()


def get_active_schedule_for_patient(db: Session, patient_id: int) -> Optional[MeasurementSchedule]:
    """Retrieve active schedule with owner."""
    return db.query(MeasurementSchedule).filter(
        MeasurementSchedule.patient_id == patient_id,
        MeasurementSchedule.is_active == True  # noqa: E712
    ).first()


def get_all_measurement_schedules(db: Session, patient_id: Optional[int] = None) -> List[MeasurementSchedule]:
    """Retrieve schedule history."""
    query = db.query(MeasurementSchedule)
    if patient_id is not None:
        query = query.filter(MeasurementSchedule.patient_id == patient_id)
    return query.order_by(MeasurementSchedule.created_at.desc()).all()


def get_measurement_schedule_by_id(db: Session, schedule_id: int) -> Optional[MeasurementSchedule]:
    """Retrieve schedule details by ID."""
    return db.query(MeasurementSchedule).filter(MeasurementSchedule.id == schedule_id).first()


def update_measurement_schedule(
    db: Session,
    schedule_id: int,
    data: Any,
    updater_role: str = "doctor",
    updated_by: Optional[int] = None,
) -> MeasurementSchedule:
    """Edit schedule: increments version and regenerates future slots."""
    schedule = get_measurement_schedule_by_id(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    from app.services.monitoring_mode_service import get_current_monitoring_mode
    current_mode = get_current_monitoring_mode(db, schedule.patient_id)
    if current_mode == "telemonitoring" and updater_role == "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SCHEDULE_OWNED_BY_DOCTOR: Only doctor can modify telemonitoring schedule"
        )

    schedule.version = (schedule.version or 1) + 1
    for field, val in data.dict(exclude_unset=True).items():
        if hasattr(schedule, field):
            setattr(schedule, field, val)
    db.commit()
    db.refresh(schedule)

    # Cancel future upcoming slots
    now = datetime.now(timezone.utc)
    future_slots = db.query(ScheduleSlot).filter(
        ScheduleSlot.schedule_id == schedule.id,
        ScheduleSlot.due_at >= now,
        ScheduleSlot.status == "upcoming"
    ).all()
    for fs in future_slots:
        db.delete(fs)
    db.commit()

    generate_slots_for_schedule(db, schedule)
    return schedule


def deactivate_measurement_schedule(db: Session, schedule_id: int) -> MeasurementSchedule:
    """Soft deactivation of schedule."""
    schedule = get_measurement_schedule_by_id(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    schedule.is_active = False
    db.commit()
    db.refresh(schedule)
    return schedule


def get_current_cycle_progress(db: Session, patient_id: int) -> Dict[str, Any]:
    """Progress of the current measurement cycle (RS-8: 722 protocol completeness)."""
    schedule = get_active_schedule_for_patient(db, patient_id)
    if not schedule:
        return {"active": False, "message": "No active measurement schedule"}

    slots = db.query(ScheduleSlot).filter(
        ScheduleSlot.schedule_id == schedule.id
    ).order_by(ScheduleSlot.due_at.asc()).all()

    total_expected_slots = len(slots)
    completed_slots = [s for s in slots if s.status == "taken"]
    partial_slots = [s for s in slots if s.status == "partial"]
    missed_slots = [s for s in slots if s.status == "missed"]

    # Days complete with both morning and evening readings taken
    by_day = {}
    for s in slots:
        day_str = s.due_at.strftime("%Y-%m-%d") if s.due_at else "unknown"
        if day_str not in by_day:
            by_day[day_str] = []
        by_day[day_str].append(s)

    complete_days = len([d for d, day_slots in by_day.items() if all(sl.status == "taken" for sl in day_slots)])

    # RS-8: Day 1 exclusion for baseline evaluation
    sorted_days = sorted(by_day.keys())
    day_1 = sorted_days[0] if sorted_days else None

    valid_readings_count = 0
    for d in sorted_days:
        if d == day_1 and schedule.protocol in ["722_diagnostic", "722_followup"]:
            continue  # exclude day 1 per 722 protocol
        for sl in by_day[d]:
            if sl.status == "taken":
                valid_readings_count += len(sl.reading_ids or [])

    meets_protocol_minimum = (valid_readings_count >= 12 and complete_days >= 3)

    return {
        "active": True,
        "protocol": schedule.protocol,
        "cycle_length_days": schedule.cycle_length_days,
        "total_slots": total_expected_slots,
        "slots_taken": len(completed_slots),
        "slots_partial": len(partial_slots),
        "slots_missed": len(missed_slots),
        "days_complete": complete_days,
        "valid_readings_count_excl_day1": valid_readings_count,
        "meets_minimum_requirements": meets_protocol_minimum,
        "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
        "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
    }


def get_past_cycles(db: Session, patient_id: int) -> List[Dict[str, Any]]:
    """List historical measurement cycles for patient."""
    schedules = db.query(MeasurementSchedule).filter(
        MeasurementSchedule.patient_id == patient_id
    ).order_by(MeasurementSchedule.created_at.desc()).all()

    past = []
    for s in schedules:
        past.append({
            "schedule_id": s.id,
            "protocol": s.protocol,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
            "is_active": s.is_active,
            "version": s.version,
        })
    return past
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
