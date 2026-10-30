"""Patient monitoring mode routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Monitoring mode records are immutable: a change creates a new record rather than
rewriting the past. Only CREATE and GET are exposed.
Access control: patients only their own; doctors only assigned patients; admins full.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.patient_service import get_patient_profile_by_user_id
from app.services.monitoring_mode_service import (
    create_monitoring_mode,
    get_monitoring_mode_by_id,
    get_monitoring_mode_by_patient,
    get_all_monitoring_modes,
)
from app.schemas.monitoring_mode import (
    PatientMonitoringModeCreate,
    PatientMonitoringModeUpdate,
    PatientMonitoringModeOut,
)

router = APIRouter(prefix="/monitoring-modes", tags=["monitoring-modes"])


def _patient_profile_for(db: Session, current_user: User):
    if current_user.role == "patient": # type: ignore
        return get_patient_profile_by_user_id(db, current_user.id) # type: ignore
    return None


def _require_mode_access(current_user: User, mode, db: Session) -> None:
    if current_user.role == "patient": # type: ignore
        check_patient_access(current_user, mode.patient_id, db)
    elif current_user.role == "doctor": # type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import is_doctor_assigned

        if not is_doctor_assigned(db, current_user.doctor_profile.id, mode.patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )


@router.get("/", response_model=List[PatientMonitoringModeOut])
def list_monitoring_modes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
):
    """List monitoring mode records (history)."""
    modes = get_all_monitoring_modes(db, skip=skip, limit=limit, patient_id=patient_id)
    if current_user.role == "patient": # type: ignore
        profile = _patient_profile_for(db, current_user)
        if not profile:
            return []
        modes = [m for m in modes if m.patient_id == profile.id] # type: ignore
    elif current_user.role == "doctor": # type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import get_all_assignments

        assignments = get_all_assignments(
            db, doctor_id=current_user.doctor_profile.id, active=True
        )
        allowed_patient_ids = {a.patient_id for a in assignments}
        modes = [m for m in modes if m.patient_id in allowed_patient_ids]
    return modes


@router.get("/{mode_id}", response_model=PatientMonitoringModeOut)
def get_monitoring_mode(
    mode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a monitoring mode record by ID."""
    mode = get_monitoring_mode_by_id(db, mode_id)
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Monitoring mode not found"
        )
    _require_mode_access(current_user, mode, db)
    return mode


@router.get("/by-patient/{patient_id}", response_model=PatientMonitoringModeOut)
def get_monitoring_mode_for_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the current monitoring mode for a patient."""
    check_patient_access(current_user, patient_id, db)
    mode = get_monitoring_mode_by_patient(db, patient_id)
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring mode not found for patient",
        )
    return mode


@router.post(
    "/",
    response_model=PatientMonitoringModeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_monitoring_mode_route(
    mode_in: PatientMonitoringModeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record a monitoring mode for a patient."""
    if current_user.role == "patient": # type: ignore
        profile = _patient_profile_for(db, current_user)
        if not profile or mode_in.patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients may only set their own monitoring mode",
            )
    mode = create_monitoring_mode(db, mode_in)
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return mode

