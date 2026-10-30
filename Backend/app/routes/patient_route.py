
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace this import with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.patient_service import (
    create_patient_profile,
    get_patient_profile_by_id,
    get_patient_profile_by_user_id,
    get_all_patient_profiles,
    update_patient_profile,
)

from app.services.assignment_service import (
    get_all_assignments,
    is_doctor_assigned,
)

from app.schemas.patient import (
    PatientProfileCreate,
    PatientProfileUpdate,
    PatientProfileOut,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


# Helper: Get current user's patient profile
def _get_current_patient_profile(
    db: Session,
    current_user: User,
):
    if current_user.role != "patient":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this resource",
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

    return profile


# Helper: Check patient profile access
def _require_patient_access(
    current_user: User,
    patient_id: int,
    db: Session,
) -> None:

    if current_user.role == "patient":# type: ignore
        profile = _get_current_patient_profile(db, current_user)

        if profile.id != patient_id:# type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another patient's profile",
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


# 1. List accessible patient profiles
@router.get("/", response_model=List[PatientProfileOut])
def list_patient_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
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

        if is_active is not None and profile.is_active != is_active:
            return []

        return [profile] if skip == 0 else []

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        assignments = get_all_assignments(
            db,
            doctor_id=current_user.doctor_profile.id,
            active=True,
        )

        allowed_patient_ids = {
            assignment.patient_id for assignment in assignments
        }

        profiles = get_all_patient_profiles(
            db,
            skip=0,
            limit=10000,
            is_active=is_active,
        )

        accessible_profiles = [
            profile
            for profile in profiles
            if profile.id in allowed_patient_ids
        ]

        return accessible_profiles[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to list patient profiles",
    )


# 2. Get patient profile by linked user ID
# Keep this route before /{profile_id}.
@router.get("/by-user/{user_id}", response_model=PatientProfileOut)
def get_patient_profile_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = get_patient_profile_by_user_id(
        db,
        user_id,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    _require_patient_access(
        current_user,
        profile.id,# type: ignore
        db,
    )

    return profile


# 3. Get patient profile by ID
@router.get("/{profile_id}", response_model=PatientProfileOut)
def get_patient_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = get_patient_profile_by_id(
        db,
        profile_id,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    _require_patient_access(
        current_user,
        profile.id,# type: ignore
        db,
    )

    return profile


# 4. Create patient profile
@router.post(
    "/",
    response_model=PatientProfileOut,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_profile_route(
    profile_in: PatientProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "patient":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create their own profile",
        )

    if profile_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients may only create their own profile",
        )

    existing_profile = get_patient_profile_by_user_id(
        db,
        current_user.id,# type: ignore
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient profile already exists",
        )

    profile = create_patient_profile(
        db,
        profile_in,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile could not be created",
        )

    return profile


# 5. Update patient profile
@router.put("/{profile_id}", response_model=PatientProfileOut)
def update_patient_profile_route(
    profile_id: int,
    profile_in: PatientProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = get_patient_profile_by_id(
        db,
        profile_id,
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    _require_patient_access(
        current_user,
        profile.id,# type: ignore
        db,
    )

    updated = update_patient_profile(
        db,
        profile_id,
        profile_in,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    return updated


# 6. Deactivate patient profile
# Disabled: profile deactivation should be handled through
# a dedicated, authorized account-management workflow.
@router.post("/{profile_id}/deactivate")
def deactivate_patient_profile_route(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Patient profile deactivation is not available",
    )

