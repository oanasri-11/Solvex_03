"""MeasurementSchedule API routes (Section 8)."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    get_current_patient,
    get_current_caregiver_or_patient,
    check_patient_access,
    resolve_acting_patient_id,
)
from app.models.user import User
from app.services.schedule_service import (
    create_measurement_schedule,
    get_active_schedule_for_patient,
    get_all_measurement_schedules,
    get_measurement_schedule_by_id,
    update_measurement_schedule,
    deactivate_measurement_schedule,
    get_recommended_protocols,
    get_current_cycle_progress,
    get_past_cycles,
)
from app.services.monitoring_mode_service import get_current_monitoring_mode
from app.schemas.schedule import (
    MeasurementScheduleCreate,
    MeasurementScheduleUpdate,
    MeasurementScheduleOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["schedules"])


# ==========================================
# Patient / Caregiver Endpoints
# ==========================================

@router.post("/patients/me/schedules", response_model=MeasurementScheduleOut, status_code=status.HTTP_201_CREATED)
def patient_create_own_schedule(
    schedule_in: MeasurementScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Create own schedule; self-monitoring only (in telemonitoring, doctor owns schedule)."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    patient_id = current_user.patient_profile.id
    mode = get_current_monitoring_mode(db, patient_id)
    mode_str = mode.mode if hasattr(mode, "mode") else str(mode)
    if mode_str == "telemonitoring":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SCHEDULE_OWNED_BY_DOCTOR: Telemonitoring schedule must be set by doctor",
        )

    return create_measurement_schedule(
        db,
        patient_id=patient_id,
        schedule_in=schedule_in,
        owner="patient",
        created_by=current_user.id,
    )


@router.get("/patients/me/schedule", response_model=Optional[MeasurementScheduleOut])
def patient_get_active_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Active schedule with owner."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_active_schedule_for_patient(db, current_user.patient_profile.id)


@router.get("/patients/me/schedules", response_model=List[MeasurementScheduleOut])
def patient_get_schedule_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Schedule history."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_all_measurement_schedules(db, patient_id=current_user.patient_profile.id)


@router.get("/patients/me/cycles/current")
def get_current_cycle_progress_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Progress of current measurement cycle: readings taken, expected, minimum met."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="view_trend")
    return get_current_cycle_progress(db, patient_id)


@router.get("/patients/me/cycles")
def get_past_cycles_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Past measurement cycles and completion rates."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_past_cycles(db, current_user.patient_profile.id)


# ==========================================
# Doctor Endpoints
# ==========================================

@router.post(
    "/doctor/patients/{id}/schedules",
    response_model=MeasurementScheduleOut,
    status_code=status.HTTP_201_CREATED,
)
def doctor_create_patient_schedule(
    id: int,
    schedule_in: MeasurementScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Define or approve a schedule for patient."""
    check_patient_access(current_user, id, db)
    return create_measurement_schedule(
        db,
        patient_id=id,
        schedule_in=schedule_in,
        owner="doctor",
        created_by=current_user.id,
    )


@router.get("/doctor/patients/{id}/schedules", response_model=List[MeasurementScheduleOut])
def doctor_get_patient_schedule_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Schedule history for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_all_measurement_schedules(db, patient_id=id)


# ==========================================
# Shared Endpoints (/schedules/{id}, protocols)
# ==========================================

@router.get("/schedule-protocols/recommended")
def get_recommended_protocols_route():
    """Protocol content from versioned config (722_diagnostic, 722_followup, maintenance)."""
    return get_recommended_protocols()


@router.get("/schedules/{id}", response_model=MeasurementScheduleOut)
def get_schedule_by_id_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Schedule details."""
    schedule = get_measurement_schedule_by_id(db, id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    check_patient_access(current_user, schedule.patient_id, db)
    return schedule


@router.patch("/schedules/{id}", response_model=MeasurementScheduleOut)
def edit_schedule_route(
    id: int,
    schedule_in: MeasurementScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Edit schedule; creates a new version and regenerates future slots."""
    schedule = get_measurement_schedule_by_id(db, id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    if current_user.role == "patient":
        if schedule.owner == "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SCHEDULE_OWNED_BY_DOCTOR: Cannot edit doctor-owned schedule",
            )
        if current_user.patient_profile.id != schedule.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "doctor":
        check_patient_access(current_user, schedule.patient_id, db)

    return update_measurement_schedule(db, id, schedule_in, updated_by=current_user.id)


@router.post("/schedules/{id}/deactivate", response_model=MessageResponse)
def deactivate_schedule_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deactivate schedule (no hard delete)."""
    schedule = get_measurement_schedule_by_id(db, id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    if current_user.role == "patient":
        if schedule.owner == "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SCHEDULE_OWNED_BY_DOCTOR: Cannot deactivate doctor-owned schedule",
            )
        if current_user.patient_profile.id != schedule.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "doctor":
        check_patient_access(current_user, schedule.patient_id, db)

    deactivate_measurement_schedule(db, id)
    return MessageResponse(message=f"Schedule {id} deactivated")
