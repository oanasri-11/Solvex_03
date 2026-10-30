
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.patient_service import get_patient_profile_by_user_id

from app.services.assignment_service import (
    is_doctor_assigned,
)

from app.services.monitoring_mode_service import (
    create_monitoring_mode,
    get_monitoring_mode_by_id,
    get_monitoring_mode_by_patient,
    get_all_monitoring_modes,
)

from app.schemas.monitoring_mode import (
    PatientMonitoringModeCreate,
    PatientMonitoringModeOut,
)

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore


router = APIRouter(
    prefix="/monitoring-modes",
    tags=["Monitoring Modes"],
)


# Helper: Check access to a patient's monitoring modes
def _require_patient_access(
    current_user: User,
    patient_id: int,
    db: Session,
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile or profile.id != patient_id:# type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own monitoring modes",
            )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        if not is_doctor_assigned(
            db,
            current_user.doctor_profile.id,
            patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# Helper: Check access to a monitoring mode record
def _require_mode_access(
    current_user: User,
    mode,
    db: Session,
):
    _require_patient_access(
        current_user,
        mode.patient_id,
        db,
    )


# 1. List monitoring mode history
@router.get("/", response_model=List[PatientMonitoringModeOut])
def list_monitoring_modes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile:
            return []

        # Ignore patient_id supplied by the client.
        return get_all_monitoring_modes(
            db,
            skip=skip,
            limit=limit,
            patient_id=profile.id,# type: ignore
        )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        modes = get_all_monitoring_modes(
            db,
            skip=0,
            limit=10000,
            patient_id=patient_id,
        )

        allowed_modes = []

        for mode in modes:
            if is_doctor_assigned(
                db,
                current_user.doctor_profile.id,
                mode.patient_id,# type: ignore
            ):
                allowed_modes.append(mode)

        return allowed_modes[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to view monitoring modes",
    )


# 2. Get monitoring mode by ID
@router.get("/{mode_id}", response_model=PatientMonitoringModeOut)
def get_monitoring_mode(
    mode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    mode = get_monitoring_mode_by_id(
        db,
        mode_id,
    )

    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring mode not found",
        )

    _require_mode_access(
        current_user,
        mode,
        db,
    )

    return mode


# 3. Get current monitoring mode for a patient
# Keep this route before /{mode_id}.
@router.get(
    "/by-patient/{patient_id}",
    response_model=PatientMonitoringModeOut,
)
def get_monitoring_mode_for_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_patient_access(
        current_user,
        patient_id,
        db,
    )

    mode = get_monitoring_mode_by_patient(
        db,
        patient_id,
    )

    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring mode not found for patient",
        )

    return mode


# 4. Create monitoring mode (doctor only)
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
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create monitoring modes",
        )

    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    _require_patient_access(
        current_user,
        mode_in.patient_id,
        db,
    )

    # Inject the authenticated doctor as the actor.
    mode_data = mode_in.model_copy(
        update={"changed_by": current_user.id}
    )

    mode = create_monitoring_mode(
        db,
        mode_data,
    )

    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return mode


