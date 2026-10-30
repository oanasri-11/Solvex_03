
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.doctor_service import (
    create_doctor_profile,
    get_doctor_profile_by_id,
    get_doctor_profile_by_user_id,
    get_all_doctors,
    update_doctor_profile,
)

from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileOut,
)

# Adjust this import to your actual authentication dependency location.
from app.core.deps import get_current_active_user# type: ignore


router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
)


# 1. List doctors
@router.get("/", response_model=List[DoctorProfileOut])
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
):
    """List doctor profiles."""
    return get_all_doctors(
        db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )


# 2. Get doctor by ID
@router.get("/{doctor_id}", response_model=DoctorProfileOut)
def get_doctor_profile(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    doctor = get_doctor_profile_by_id(db, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    return doctor


# 3. Get doctor by linked user ID
# Keep this route before /{doctor_id} to avoid route conflicts.
@router.get("/by-user/{user_id}", response_model=DoctorProfileOut)
def get_doctor_profile_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    doctor = get_doctor_profile_by_user_id(db, user_id)

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    return doctor


# 4. Create doctor profile (doctor only)
@router.post(
    "/",
    response_model=DoctorProfileOut,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_profile_route(
    doctor_in: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create doctor profiles",
        )

    if doctor_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors may only create their own profile",
        )

    doctor = create_doctor_profile(db, doctor_in)

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked user not found or profile already exists",
        )

    return doctor


# 5. Update doctor profile (owner only)
@router.put("/{doctor_id}", response_model=DoctorProfileOut)
def update_doctor_profile_route(
    doctor_id: int,
    doctor_in: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    doctor = get_doctor_profile_by_id(db, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update doctor profiles",
        )

    if not current_user.doctor_profile or current_user.doctor_profile.id != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors may only update their own profile",
        )

    updated = update_doctor_profile(
        db,
        doctor_id,
        doctor_in,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    return updated


