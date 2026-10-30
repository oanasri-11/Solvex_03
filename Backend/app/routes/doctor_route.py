"""Doctor profile routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Access control:
- Doctors may manage their own profile; admins have full access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
)
from app.models.user import User
from app.services.doctor_service import (
    create_doctor_profile,
    get_doctor_profile_by_id,
    get_doctor_profile_by_user_id,
    get_all_doctors,
    update_doctor_profile,
    deactivate_doctor_profile,
)
from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileOut,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/", response_model=List[DoctorProfileOut])
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
):
    """List doctor profiles (admins and active users)."""
    return get_all_doctors(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/{doctor_id}", response_model=DoctorProfileOut)
def get_doctor_profile(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a doctor profile by ID."""
    doctor = get_doctor_profile_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
        )
    return doctor


@router.get("/by-user/{user_id}", response_model=DoctorProfileOut)
def get_doctor_profile_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a doctor profile by the linked user ID."""
    doctor = get_doctor_profile_by_user_id(db, user_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
        )
    return doctor


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
    """Create a doctor profile (admin/doctor)."""
    if current_user.role not in ("admin", "doctor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or doctors may create doctor profiles",
        )
    if current_user.role == "doctor" and doctor_in.user_id != current_user.id: # type: ignore
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


@router.put("/{doctor_id}", response_model=DoctorProfileOut)
def update_doctor_profile_route(
    doctor_id: int,
    doctor_in: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a doctor profile."""
    doctor = get_doctor_profile_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
        )
    if (
        current_user.role == "doctor" # type: ignore
        and current_user.doctor_profile
        and current_user.doctor_profile.id != doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors may only update their own profile",
        )
    updated = update_doctor_profile(db, doctor_id, doctor_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
        )
    return updated


@router.post("/{doctor_id}/deactivate", response_model=DoctorProfileOut)
def deactivate_doctor_profile_route(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deactivate a doctor profile (admin only; refused while active assignments exist)."""
    if current_user.role != "admin": # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins may deactivate doctor profiles",
        )
    doctor = get_doctor_profile_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
        )
    deactivated = deactivate_doctor_profile(db, doctor_id)
    if deactivated is None:
        # Could be not found or active assignments exist; service returns None for both.
        active = (
            db.query(__import__("app.models.DoctorPatientAssignment", fromlist=["DoctorPatientAssignment"]).DoctorPatientAssignment)
            .filter_by(doctor_id=doctor_id, is_active=True)
            .first()
        )
        if active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot deactivate: active patient assignments exist",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
        )
    return deactivated

