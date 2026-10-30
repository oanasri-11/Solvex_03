
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.reading_service import (
    create_blood_pressure_reading,
    get_blood_pressure_reading_by_id,
    get_all_blood_pressure_readings,
)

from app.services.patient_service import (
    get_patient_profile_by_user_id,
)

from app.services.assignment_service import (
    is_doctor_assigned,
    get_all_assignments,
)

from app.schemas.measurement import (
    BloodPressureReadingCreate,
    BloodPressureReadingOut,
)


router = APIRouter(
    prefix="/readings",
    tags=["Readings"],
)


# Helper: Check access to a reading
def _require_reading_access(
    current_user: User,
    reading,
    db: Session,
) -> None:

    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile or profile.id != reading.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another patient's reading",
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
            reading.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reading not found or patient not assigned to doctor",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# 1. List accessible readings
@router.get("/", response_model=List[BloodPressureReadingOut])
def list_readings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile:
            return []

        # Patients cannot request another patient's readings.
        if patient_id is not None and patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own readings",
            )

        return get_all_blood_pressure_readings(
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

        # If a patient ID is specified, verify assignment.
        if patient_id is not None:
            if not is_doctor_assigned(
                db,
                current_user.doctor_profile.id,
                patient_id,
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found or not assigned to doctor",
                )

            return get_all_blood_pressure_readings(
                db,
                skip=skip,
                limit=limit,
                patient_id=patient_id,
            )

        # Otherwise, retrieve readings for assigned patients.
        assignments = get_all_assignments(
            db,
            doctor_id=current_user.doctor_profile.id,
            active=True,
        )

        allowed_patient_ids = {
            assignment.patient_id for assignment in assignments
        }

        readings = get_all_blood_pressure_readings(
            db,
            skip=0,
            limit=10000,
        )

        accessible_readings = [
            reading
            for reading in readings
            if reading.patient_id in allowed_patient_ids
        ]

        return accessible_readings[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access readings",
    )


# 2. Get reading by ID
@router.get("/{reading_id}", response_model=BloodPressureReadingOut)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    reading = get_blood_pressure_reading_by_id(
        db,
        reading_id,
    )

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading not found",
        )

    _require_reading_access(
        current_user,
        reading,
        db,
    )

    return reading


# 3. Create a new blood pressure reading
@router.post(
    "/",
    response_model=BloodPressureReadingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_reading_route(
    reading_in: BloodPressureReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "patient":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can submit readings",
        )

    profile = get_patient_profile_by_user_id(
        db,
        current_user.id,# type: ignore
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    if reading_in.patient_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients may only create readings for themselves",
        )

    reading = create_blood_pressure_reading(
        db,
        reading_in,
    )

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reading could not be created",
        )

    return reading

