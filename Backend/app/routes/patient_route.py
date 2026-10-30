"""Patient profile routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Access control:
- Patients may only access their own profile.
- Doctors may only access profiles of patients assigned to them.
- Admins have full access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    get_current_admin,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.patient_service import (
    create_patient_profile,
    get_patient_profile_by_id,
    get_patient_profile_by_user_id,
    get_all_patient_profiles,
    update_patient_profile,
    deactivate_patient_profile,
)
from app.schemas.patient import (
    PatientProfileCreate,
    PatientProfileUpdate,
    PatientProfileOut,
)

router = APIRouter(prefix="/patients", tags=["patients"])


def _require_patient_access(current_user: User, patient_id: int, db: Session) -> None:
    """Enforce patient-record access rules."""
    check_patient_access(current_user, patient_id, db)


@router.get("/", response_model=List[PatientProfileOut])
def list_patient_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
):
    """List patient profiles.

    - Admins: all profiles.
    - Doctors: profiles of their assigned patients.
    - Patients: only their own profile.
    """
    profiles = get_all_patient_profiles(db, skip=skip, limit=limit, is_active=is_active)

    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(db, current_user.id)# type: ignore
        if not profile:
            return []
        profiles = [p for p in profiles if p.id == profile.id]# type: ignore
    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )
        from app.services.assignment_service import get_all_assignments

        assignments = get_all_assignments(
            db, doctor_id=current_user.doctor_profile.id, active=True
        )
        allowed_patient_ids = {a.patient_id for a in assignments}
        profiles = [p for p in profiles if p.user_id in allowed_patient_ids]

    return profiles


@router.get("/{profile_id}", response_model=PatientProfileOut)
def get_patient_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a patient profile by ID."""
    profile = get_patient_profile_by_id(db, profile_id)
    if not profile:
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
    """Create a patient profile.

    Patients may only create their own profile; admins/doctors may create for others.
    """
    if current_user.role == "patient" and profile_in.user_id != current_user.id:# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients may only create their own profile",
        )
    profile = create_patient_profile(db, profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked user not found or profile already exists",
        )
    return profile


@router.put("/{profile_id}", response_model=PatientProfileOut)
def update_patient_profile_route(
    profile_id: int,
    profile_in: PatientProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a patient profile."""
    profile = get_patient_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
    _require_patient_access(current_user, profile.id, db)# type: ignore
    updated = update_patient_profile(db, profile_id, profile_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
    return updated


@router.post("/{profile_id}/deactivate", response_model=PatientProfileOut)
def deactivate_patient_profile_route(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deactivate a patient profile (soft delete via linked user)."""
    profile = get_patient_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
    _require_patient_access(current_user, profile.id, db)# type: ignore
    if current_user.role not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins may deactivate patient profiles",
        )
    deactivated = deactivate_patient_profile(db, profile_id)
    if not deactivated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
    return deactivated

raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
require_patient_access(current_user, profile.id, db)
 return profile# type: ignore 


@router.get("/by-user/{user_id}", response_model=PatientProfileOut)
def get_patient_profile_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a patient profile by the linked user ID."""
    profile = get_patient_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
    _require_patient_access(current_user, profile.id, db)
    return profile

