"""DoctorProfile service (Section 3)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.doctorprofile import DoctorProfile
from app.models.user import User
from app.models.DoctorPatientAssignment import DoctorPatientAssignment


def create_doctor_profile(db: Session, doctor_in: Any) -> DoctorProfile:
    """Create a doctor profile."""
    user = db.query(User).filter(User.id == doctor_in.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.query(DoctorProfile).filter(DoctorProfile.user_id == doctor_in.user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Doctor profile already exists")

    profile = DoctorProfile(
        user_id=doctor_in.user_id,
        first_name=getattr(doctor_in, "first_name", None) or getattr(user, "full_name", "").split(" ")[0],
        last_name=getattr(doctor_in, "last_name", None) or (getattr(user, "full_name", "").split(" ")[1] if " " in getattr(user, "full_name", "") else ""),
        license_number=doctor_in.license_number,
        specialization=getattr(doctor_in, "specialization", None),
        speciality=getattr(doctor_in, "speciality", None) or getattr(doctor_in, "specialization", None),
        facility=getattr(doctor_in, "facility", None),
        phone=getattr(doctor_in, "phone", None) or getattr(user, "phone", None),
        is_active=True,
        notification_preferences={
            "critical_emergency": ["in_app", "sms"],
            "severe_single_reading": ["in_app", "email"],
            "persistent_elevation": ["in_app"],
            "routine_out_of_range": ["in_app"],
        }
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_doctor_profile_by_id(db: Session, doctor_id: int) -> Optional[DoctorProfile]:
    """Get doctor profile by ID."""
    return db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()


def get_doctor_profile_by_user_id(db: Session, user_id: int) -> Optional[DoctorProfile]:
    """Get doctor profile by user ID."""
    return db.query(DoctorProfile).filter(DoctorProfile.user_id == user_id).first()


def get_all_doctors(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> List[DoctorProfile]:
    """List doctors."""
    query = db.query(DoctorProfile)
    if is_active is not None:
        query = query.filter(DoctorProfile.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def update_doctor_profile(db: Session, doctor_id: int, update_in: Any) -> Optional[DoctorProfile]:
    """Update own profile."""
    profile = get_doctor_profile_by_id(db, doctor_id)
    if not profile:
        return None
    for field, val in update_in.dict(exclude_unset=True).items():
        if hasattr(profile, field):
            setattr(profile, field, val)
    db.commit()
    db.refresh(profile)
    return profile


def get_notification_preferences(db: Session, doctor_id: int) -> Dict[str, Any]:
    """Retrieve notification channel preferences per response tier."""
    profile = get_doctor_profile_by_id(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")

    return profile.notification_preferences or {
        "critical_emergency": ["in_app", "sms"],
        "severe_single_reading": ["in_app", "email"],
        "persistent_elevation": ["in_app"],
    }


def update_notification_preferences(db: Session, doctor_id: int, prefs: Dict[str, Any]) -> Dict[str, Any]:
    """Replace notification settings; critical tier must keep at least two channels (Section 3)."""
    profile = get_doctor_profile_by_id(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")

    critical_channels = prefs.get("critical_emergency", [])
    if len(critical_channels) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Critical tier must keep at least two notification channels (e.g., in_app and sms)"
        )

    profile.notification_preferences = prefs
    db.commit()
    db.refresh(profile)
    return profile.notification_preferences


def get_patient_doctor_info(db: Session, patient_id: int) -> Optional[Dict[str, Any]]:
    """Patient-facing view of assigned doctor: name and speciality only."""
    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).first()

    if not assignment:
        return None

    doc = db.query(DoctorProfile).filter(DoctorProfile.id == assignment.doctor_id).first()
    if not doc:
        return None

    return {
        "id": doc.id,
        "name": f"Dr. {doc.first_name or ''} {doc.last_name or ''}".strip(),
        "speciality": doc.speciality or doc.specialization,
        "facility": doc.facility,
    }


def deactivate_doctor_profile(db: Session, doctor_id: int) -> bool:
    """Soft deactivate doctor; refused while active assignments exist unless reassigned."""
    profile = get_doctor_profile_by_id(db, doctor_id)
    if not profile:
        return False

    active_assignments = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).count()

    if active_assignments > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot deactivate doctor with {active_assignments} active patient assignments. Reassign patients first."
        )

    profile.is_active = False
    db.commit()
    return True
