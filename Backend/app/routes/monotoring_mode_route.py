<<<<<<< HEAD
"""Patient monitoring mode routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Monitoring mode records are immutable: a change creates a new record rather than
rewriting the past. Only CREATE and GET are exposed.
Access control: patients only their own; doctors only assigned patients; admins full.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
=======
"""Monitoring Mode API routes (Section 5)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query, Body
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
<<<<<<< HEAD
    get_current_admin,
=======
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
<<<<<<< HEAD
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

=======
from app.services.monitoring_mode_service import (
    get_current_monitoring_mode,
    get_monitoring_mode_history,
    assign_monitoring_mode,
    get_mode_suitability,
    request_mode_change,
    get_mode_change_requests_for_patient,
    get_pending_requests_for_doctor,
    resolve_mode_change_request,
)
from app.schemas.monitoring_mode import (
    PatientMonitoringModeCreate,
    PatientMonitoringModeOut,
)
from app.schemas.mode_change_request import (
    ModeChangeRequestCreate,
    ModeChangeResolveRequest,
    ModeChangeRequestOut,
)

router = APIRouter(tags=["monitoring_mode"])


# ==========================================
# Patient-Side Endpoints (/patients/me/monitoring-mode*)
# ==========================================

@router.get("/patients/me/monitoring-mode", response_model=Optional[PatientMonitoringModeOut])
def patient_get_current_mode(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Current active monitoring mode for the patient."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_current_monitoring_mode(db, current_user.patient_profile.id)


@router.get("/patients/me/monitoring-modes", response_model=List[PatientMonitoringModeOut])
def patient_get_mode_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Monitoring mode history (read-only)."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_monitoring_mode_history(db, current_user.patient_profile.id)


@router.post("/patients/me/monitoring-mode-requests", response_model=ModeChangeRequestOut, status_code=status.HTTP_201_CREATED)
def patient_request_mode_change(
    req_in: ModeChangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Patient asks for a mode change."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    try:
        return request_mode_change(
            db,
            patient_id=current_user.patient_profile.id,
            requested_mode=req_in.requested_mode,
            reason=req_in.reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/patients/me/monitoring-mode-requests", response_model=List[ModeChangeRequestOut])
def patient_get_own_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Own mode change requests and status."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_mode_change_requests_for_patient(db, current_user.patient_profile.id)


# ==========================================
# Doctor-Side Endpoints
# ==========================================

@router.get("/doctor/patients/{id}/monitoring-modes", response_model=List[PatientMonitoringModeOut])
def doctor_get_patient_mode_history(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Patient mode history for doctor."""
    check_patient_access(current_user, id, db)
    return get_monitoring_mode_history(db, id)


@router.post("/doctor/patients/{id}/monitoring-modes", response_model=PatientMonitoringModeOut)
def doctor_set_patient_mode(
    id: int,
    mode_in: PatientMonitoringModeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Set or change mode; closes previous record; recalculates priority and flips schedule ownership."""
    check_patient_access(current_user, id, db)
    try:
        return assign_monitoring_mode(
            db,
            patient_id=id,
            mode=mode_in.mode,
            changed_by=current_user.id,
            consent_id=getattr(mode_in, "consent_id", None),
            reason=getattr(mode_in, "reason", None),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/doctor/patients/{id}/monitoring-mode/suitability")
def doctor_get_suitability(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Decision support: factors for and against telemonitoring."""
    check_patient_access(current_user, id, db)
    return get_mode_suitability(db, id)


@router.get("/doctor/me/monitoring-mode-requests", response_model=List[ModeChangeRequestOut])
def doctor_get_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    status_filter: Optional[str] = Query("pending", alias="status"),
):
    """Pending mode change requests across assigned patients."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return get_pending_requests_for_doctor(db, current_user.doctor_profile.id, status=status_filter)


@router.post("/monitoring-mode-requests/{id}/resolve", response_model=ModeChangeRequestOut)
def doctor_resolve_mode_request(
    id: int,
    resolve_in: ModeChangeResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Resolve patient mode change request (approved or declined)."""
    try:
        req = resolve_mode_change_request(
            db,
            request_id=id,
            decision=resolve_in.decision,
            note=resolve_in.note,
            doctor_user_id=current_user.id,
        )
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        return req
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
