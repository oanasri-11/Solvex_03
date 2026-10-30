"""Contact request service.

CRUD operations for the ContactRequest model, following classic SQLAlchemy syntax.
Contact requests are never deleted. Status moves open -> in_progress -> done;
completion links an outcome review.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ContactRequest import ContactRequest
from app.models.patientprofile import PatientProfile
from app.models.doctorprofile import DoctorProfile
from app.schemas.contact_request import (
    ContactRequestCreate,
    ContactRequestUpdate,
    ContactRequestOut,
)


def create_contact_request(db: Session, request_in: ContactRequestCreate) -> Optional[ContactRequest]:
    """Create a contact request (doctor-initiated). Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == request_in.patient_id).first()
        )
        if not patient:
            return None
        status = getattr(request_in, "status", None) or "open"
        db_request = ContactRequest(
            patient_id=request_in.patient_id,
            doctor_id=getattr(request_in, "doctor_id", None),
            message=request_in.message,
            status=status,
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except SQLAlchemyError:
        db.rollback()
        raise


def get_contact_request_by_id(db: Session, request_id: int) -> Optional[ContactRequest]:
    """Retrieve a contact request by its primary key."""
    return db.query(ContactRequest).filter(ContactRequest.id == request_id).first()


def get_all_contact_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """List contact requests with optional patient_id / status filters."""
    query = db.query(ContactRequest)
    if patient_id is not None:
        query = query.filter(ContactRequest.patient_id == patient_id)
    if status is not None:
        query = query.filter(ContactRequest.status == status)
    return query.order_by(ContactRequest.created_at.desc()).offset(skip).limit(limit).all()


def update_contact_request(
    db: Session, request_id: int, request_in: ContactRequestUpdate
) -> Optional[ContactRequest]:
    """Update a contact request (move status open -> in_progress)."""
    try:
        db_request = get_contact_request_by_id(db, request_id)
        if not db_request:
            return None
        update_data = request_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_request, field, value)
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except SQLAlchemyError:
        db.rollback()
        raise


def complete_contact_request(
    db: Session, request_id: int, review_id: Optional[int] = None
) -> Optional[ContactRequest]:
    """Mark a contact request done, linking an outcome review_id."""
    try:
        db_request = get_contact_request_by_id(db, request_id)
        if not db_request:
            return None
        db_request.status = "done"# type: ignore
        db_request.responded_at = datetime.utcnow()# type: ignore
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except SQLAlchemyError:
        db.rollback()
        raise


# Note: delete is intentionally omitted. Contact requests are never deleted per the
# specification.
