"""Patient service.

CRUD operations for the PatientProfile model, following classic SQLAlchemy syntax.
Deactivation is performed through the linked User record (soft delete only).
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.patientprofile import PatientProfile
from app.models.user import User
from app.schemas.patient import PatientProfileCreate, PatientProfileUpdate, PatientProfileOut


def create_patient_profile(db: Session, profile_in: PatientProfileCreate) -> Optional[PatientProfile]:
    """Create a new patient profile linked to an existing user."""
    try:
        user = db.query(User).filter(User.id == profile_in.user_id).first()
        if not user:
            return None
        existing = (
            db.query(PatientProfile)
            .filter(PatientProfile.user_id == profile_in.user_id)
            .first()
        )
        if existing:
            return existing
        db_profile = PatientProfile(
            user_id=profile_in.user_id,
            date_of_birth=getattr(profile_in, "date_of_birth", None),
            gender=getattr(profile_in, "gender", None),
            phone=getattr(profile_in, "phone", None),
            address=getattr(profile_in, "address", None),
            emergency_contact_name=getattr(profile_in, "emergency_contact_name", None),
            emergency_contact_phone=getattr(profile_in, "emergency_contact_phone", None),
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError:
        db.rollback()
        raise


def get_patient_profile_by_id(db: Session, profile_id: int) -> Optional[PatientProfile]:
    """Retrieve a patient profile by its primary key."""
    return db.query(PatientProfile).filter(PatientProfile.id == profile_id).first()


def get_patient_profile_by_user_id(db: Session, user_id: int) -> Optional[PatientProfile]:
    """Retrieve a patient profile by the linked user id."""
    return db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()


def get_all_patient_profiles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
):
    """List patient profiles with an optional is_active filter."""
    query = db.query(PatientProfile)
    if is_active is not None:
        query = query.join(User, PatientProfile.user_id == User.id).filter(
            User.is_active == is_active
        )
    return query.offset(skip).limit(limit).all()


def update_patient_profile(
    db: Session, profile_id: int, profile_in: PatientProfileUpdate
) -> Optional[PatientProfile]:
    """Update contact details and preferences of a patient profile."""
    try:
        db_profile = get_patient_profile_by_id(db, profile_id)
        if not db_profile:
            return None
        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError:
        db.rollback()
        raise


def deactivate_patient_profile(db: Session, profile_id: int) -> Optional[PatientProfile]:
    """Soft deactivate a patient by deactivating its linked user (keeps all data)."""
    try:
        db_profile = get_patient_profile_by_id(db, profile_id)
        if not db_profile:
            return None
        db_user = db.query(User).filter(User.id == db_profile.user_id).first()
        if db_user:
            db_user.is_active = False# type: ignore
            db.add(db_user)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError:
        db.rollback()
        raise
