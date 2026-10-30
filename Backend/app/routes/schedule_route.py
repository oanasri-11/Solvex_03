<<<<<<< HEAD
"""Measurement schedule routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Only one schedule is active per patient; deactivation is soft (no hard delete).
Access control: patients only their own; doctors only assigned patients; admins full.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
=======
"""MeasurementSchedule API routes (Section 8)."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
<<<<<<< HEAD
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.patient_service import get_patient_profile_by_user_id
from app.services.schedule_service import (
    create_measurement_schedule,
    get_measurement_schedule_by_id,
    get_all_measurement_schedules,
    get_active_schedule_for_patient,
    update_measurement_schedule,
    deactivate_measurement_schedule,
)
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from app.schemas.schedule import (
    MeasurementScheduleCreate,
    MeasurementScheduleUpdate,
    MeasurementScheduleOut,
)
<<<<<<< HEAD

router = APIRouter(prefix="/schedules", tags=["schedules"])


def _patient_profile_for(db: Session, current_user: User):
    if current_user.role == "patient":# type: ignore
        return get_patient_profile_by_user_id(db, current_user.id)# type: ignore
    return None


def _require_schedule_access(current_user: User, schedule, db: Session) -> None:
    if current_user.role == "patient":# type: ignore
        check_patient_access(current_user, schedule.patient_id, db)
    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import is_doctor_assigned

        if not is_doctor_assigned(db, current_user.doctor_profile.id, schedule.patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )


@router.get("/", response_model=List[MeasurementScheduleOut])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
@router.get("/by-patient/{patient_id}/active", response_model=MeasurementScheduleOut)
def get_active_schedule(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),# type: ignore
):
    """Get the active measurement schedule for a patient."""
    check_patient_access(current_user, patient_id, db)
    schedule = get_active_schedule_for_patient(db, patient_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active schedule found for patient",
        )
    return schedule


@router.post(
    "/",
    response_model=MeasurementScheduleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule_route(
    schedule_in: MeasurementScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Define a measurement schedule for a patient."""
    if current_user.role == "patient":
        profile = _patient_profile_for(db, current_user)
        if not profile or schedule_in.patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients may only create schedules for themselves",
            )
    schedule = create_measurement_schedule(db, schedule_in)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return schedule


@router.put("/{schedule_id}", response_model=MeasurementScheduleOut)
def update_schedule_route(
    schedule_id: int,
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    schedule_in: MeasurementScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
<<<<<<< HEAD
    
    schedule = get_measurement_schedule_by_id(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
    _require_schedule_access(current_user, schedule, db)
    updated = update_measurement_schedule(db, schedule_id, schedule_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
    return updated


@router.post("/{schedule_id}/deactivate", response_model=MeasurementScheduleOut)
def deactivate_schedule_route(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    
    schedule = get_measurement_schedule_by_id(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
    _require_schedule_access(current_user, schedule, db)
    deactivated = deactivate_measurement_schedule(db, schedule_id)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
    return deactivated

    is_active: Optional[bool] = Query(None),
):
    """List measurement schedules."""# type: ignore
    schedules = get_all_measurement_schedules(# type: ignore
        db, skip=skip, limit=limit, patient_id=patient_id, is_active=is_active# type: ignore
    )
    if current_user.role == "patient":# type: ignore
        profile = _patient_profile_for(db, current_user)# type: ignore
        if not profile:
            return []# type: ignore
        schedules = [s for s in schedules if s.patient_id == profile.id]# type: ignore
    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:# type: ignore
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import get_all_assignments

        assignments = get_all_assignments(
            db, doctor_id=current_user.doctor_profile.id, active=True# type: ignore
        )
        allowed_patient_ids = {a.patient_id for a in assignments}
        schedules = [s for s in schedules if s.patient_id in allowed_patient_ids]
    return schedules# type: ignore


@router.get("/{schedule_id}", response_model=MeasurementScheduleOut)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a measurement schedule by ID."""
    schedule = get_measurement_schedule_by_id(db, schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found"
        )
    _require_schedule_access(current_user, schedule, db)
    return schedule

=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
