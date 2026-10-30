
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.patient_service import (
    get_patient_profile_by_user_id,
)

from app.services.assignment_service import (
    is_doctor_assigned,
    get_all_assignments,
)

from app.services.schedule_service import (
    create_measurement_schedule,
    get_measurement_schedule_by_id,
    get_all_measurement_schedules,
    get_active_schedule_for_patient,
    update_measurement_schedule,
    deactivate_measurement_schedule,
)

from app.schemas.schedule import (
    MeasurementScheduleCreate,
    MeasurementScheduleUpdate,
    MeasurementScheduleOut,
)


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


# Helper: Get current patient's profile
def _patient_profile_for(
    db: Session,
    current_user: User,
):
    if current_user.role != "patient":# type: ignore
        return None

    return get_patient_profile_by_user_id(
        db,
        current_user.id,# type: ignore
    )


# Helper: Check doctor assignment
def _require_doctor_assignment(
    db: Session,
    current_user: User,
    patient_id: int,
) -> None:

    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )

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


# Helper: Check schedule access
def _require_schedule_access(
    current_user: User,
    schedule,
    db: Session,
) -> None:

    if current_user.role == "patient":# type: ignore
        profile = _patient_profile_for(db, current_user)

        if not profile or profile.id != schedule.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another patient's schedule",
            )

    elif current_user.role == "doctor":# type: ignore
        _require_doctor_assignment(
            db,
            current_user,
            schedule.patient_id,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access schedules",
        )


# 1. List accessible schedules
@router.get("/", response_model=List[MeasurementScheduleOut])
def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "patient":# type: ignore
        profile = _patient_profile_for(db, current_user)

        if not profile:
            return []

        if patient_id is not None and patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own schedules",
            )

        return get_all_measurement_schedules(
            db,
            skip=skip,
            limit=limit,
            patient_id=profile.id,# type: ignore
            is_active=is_active,
        )

    elif current_user.role == "doctor":# type: ignore
        # type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        if patient_id is not None:
            _require_doctor_assignment(
                db,
                current_user,
                patient_id,
            )

            return get_all_measurement_schedules(
                db,
                skip=skip,
                limit=limit,
                patient_id=patient_id,
                is_active=is_active,
            )

        assignments = get_all_assignments(
            db,
            doctor_id=current_user.doctor_profile.id,
            active=True,
        )

        allowed_patient_ids = {
            assignment.patient_id for assignment in assignments
        }

        schedules = get_all_measurement_schedules(
            db,
            skip=0,
            limit=10000,
            is_active=is_active,
        )

        accessible_schedules = [
            schedule
            for schedule in schedules
            if schedule.patient_id in allowed_patient_ids
        ]

        return accessible_schedules[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to list schedules",
    )


# 2. Get active schedule for a patient
@router.get(
    "/by-patient/{patient_id}/active",
    response_model=MeasurementScheduleOut,
)
def get_active_schedule(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "patient":# type: ignore
        profile = _patient_profile_for(db, current_user)

        if not profile or profile.id != patient_id:# type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own schedule",
            )

    elif current_user.role == "doctor":# type: ignore
        _require_doctor_assignment(
            db,
            current_user,
            patient_id,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    schedule = get_active_schedule_for_patient(
        db,
        patient_id,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active schedule found for patient",
        )

    return schedule


# 3. Create schedule (doctor only)
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
    _require_doctor_assignment(
        db,
        current_user,
        schedule_in.patient_id,
    )

    schedule = create_measurement_schedule(
        db,
        schedule_in,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient not found or active schedule already exists",
        )

    return schedule


# 4. Update schedule (doctor only)
@router.put(
    "/{schedule_id}",
    response_model=MeasurementScheduleOut,
)
def update_schedule_route(
    schedule_id: int,
    schedule_in: MeasurementScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    schedule = get_measurement_schedule_by_id(
        db,
        schedule_id,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    _require_doctor_assignment(
        db,
        current_user,
        schedule.patient_id,# type: ignore
    )

    updated = update_measurement_schedule(
        db,
        schedule_id,
        schedule_in,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return updated


# 5. Deactivate schedule (doctor only)
@router.post(
    "/{schedule_id}/deactivate",
    response_model=MeasurementScheduleOut,
)
def deactivate_schedule_route(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    schedule = get_measurement_schedule_by_id(
        db,
        schedule_id,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    _require_doctor_assignment(
        db,
        current_user,
        schedule.patient_id,# type: ignore
    )

    deactivated = deactivate_measurement_schedule(
        db,
        schedule_id,
    )

    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return deactivated


# 6. Get schedule by ID
@router.get(
    "/{schedule_id}",
    response_model=MeasurementScheduleOut,
)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    schedule = get_measurement_schedule_by_id(
        db,
        schedule_id,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    _require_schedule_access(
        current_user,
        schedule,
        db,
    )

    return schedule


