<<<<<<< HEAD
"""Doctor profile routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Access control:
- Doctors may manage their own profile; admins have full access.
"""

from typing import List, Optional
=======
"""DoctorProfile API routes (Section 3)."""

from typing import List, Optional, Dict, Any
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
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
<<<<<<< HEAD
    get_doctor_profile_by_id,
    get_doctor_profile_by_user_id,
    get_all_doctors,
    update_doctor_profile,
    deactivate_doctor_profile,
=======
    get_all_doctors,
    get_doctor_profile_by_id,
    get_doctor_profile_by_user_id,
    update_doctor_profile,
    deactivate_doctor_profile,
    get_notification_preferences,
    update_notification_preferences,
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
)
from app.schemas.doctor import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileOut,
<<<<<<< HEAD
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

=======
    DoctorNotificationPreferencesUpdate,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["doctors"])


# ==========================================
# Doctor Own Profile Endpoints (/doctors/me, /doctor/me/...)
# ==========================================

@router.get("/doctors/me", response_model=DoctorProfileOut)
def get_own_doctor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Doctor retrieves own profile."""
    profile = get_doctor_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return profile


@router.patch("/doctors/me", response_model=DoctorProfileOut)
def update_own_doctor_profile(
    profile_in: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Doctor updates own profile."""
    profile = get_doctor_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return update_doctor_profile(db, profile.id, profile_in)


@router.get("/doctor/me/notification-preferences")
def get_own_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Channels for active alert notification (in_app, email, sms) per response tier."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return get_notification_preferences(db, current_user.doctor_profile.id)


@router.put("/doctor/me/notification-preferences")
def update_own_notification_preferences(
    prefs: DoctorNotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Replace the settings; critical tier always keeps at least two channels."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    try:
        updated = update_notification_preferences(
            db, current_user.doctor_profile.id, prefs.model_dump()
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ==========================================
# Administrator Doctor Endpoints (/doctors)
# ==========================================

@router.post("/doctors", response_model=DoctorProfileOut, status_code=status.HTTP_201_CREATED)
def admin_create_doctor(
    profile_in: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create a doctor profile - Admin only."""
    try:
        return create_doctor_profile(db, profile_in)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/doctors", response_model=List[DoctorProfileOut])
def admin_list_doctors(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = Query(None),
):
    """List doctor profiles - Admin only."""
    return get_all_doctors(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/doctors/{id}", response_model=DoctorProfileOut)
def admin_get_doctor(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Read a doctor profile - Admin only."""
    profile = get_doctor_profile_by_id(db, id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return profile


@router.delete("/doctors/{id}", response_model=MessageResponse)
def admin_deactivate_doctor(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Deactivate doctor; refused while active assignments exist unless reassigned."""
    try:
        deactivate_doctor_profile(db, id)
        return MessageResponse(message=f"Doctor {id} deactivated successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
