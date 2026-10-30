"""Doctor service.

CRUD operations for the DoctorProfile model, following classic SQLAlchemy syntax.
Deactivation is performed through the linked User record (soft delete only) and is
refused while active doctor-patient assignments exist.
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.doctorprofile import DoctorProfile
from app.models.user import User
from app.schemas.doctor import DoctorProfileCreate, DoctorProfileUpdate, DoctorProfileOut


def create_doctor_profile(db: Session, doctor_in: DoctorProfileCreate) -> Optional[DoctorProfile]:
    """Create a new doctor profile linked to an existing user."""
    try:
        user = db.query(User).filter(User.id == doctor_in.user_id).first()
        if not user:
            return None
        existing = (
            db.query(DoctorProfile)
            .filter(DoctorProfile.user_id == doctor_in.user_id)
            .first()
        )
        if existing:
            return existing
        db_doctor = DoctorProfile(
            user_id=doctor_in.user_id,
            license_number=doctor_in.license_number,
            specialization=getattr(doctor_in, "specialization", None),
            phone=getattr(doctor_in, "phone", None),
        )
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except SQLAlchemyError:
        db.rollback()
        raise


def get_doctor_profile_by_id(db: Session, doctor_id: int) -> Optional[DoctorProfile]:
    """Retrieve a doctor profile by its primary key."""
    return db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()


def get_doctor_profile_by_user_id(db: Session, user_id: int) -> Optional[DoctorProfile]:
    """Retrieve a doctor profile by the linked user id."""
    return db.query(DoctorProfile).filter(DoctorProfile.user_id == user_id).first()


def get_all_doctors(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
):
    """List doctor profiles with an optional is_active filter."""
    query = db.query(DoctorProfile)
    if is_active is not None:
        query = query.join(User, DoctorProfile.user_id == User.id).filter(
            User.is_active == is_active
        )
    return query.offset(skip).limit(limit).all()


def update_doctor_profile(
    db: Session, doctor_id: int, doctor_in: DoctorProfileUpdate
) -> Optional[DoctorProfile]:
    """Update a doctor profile."""
    try:
        db_doctor = get_doctor_profile_by_id(db, doctor_id)
        if not db_doctor:
            return None
        update_data = doctor_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_doctor, field, value)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except SQLAlchemyError:
        db.rollback()
        raise


def deactivate_doctor_profile(db: Session, doctor_id: int) -> Optional[DoctorProfile]:
    """Soft deactivate a doctor (via linked user) unless active assignments exist."""
    try:
        db_doctor = get_doctor_profile_by_id(db, doctor_id)
        if not db_doctor:
            return None
        active_assignment = (
            db.query(DoctorPatientAssignment)
            .filter(
                DoctorPatientAssignment.doctor_id == doctor_id,
                DoctorPatientAssignment.is_active == True,  # noqa: E712
            )
            .first()
        )
        if active_assignment:
            return None
        db_user = db.query(User).filter(User.id == db_doctor.user_id).first()
        if db_user:
            db_user.is_active = False# type: ignore
            db.add(db_user)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except SQLAlchemyError:
        db.rollback()
        raise
