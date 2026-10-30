<<<<<<< HEAD


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

=======
"""ContactRequest service (Section 18, UC19a, UC19b, F19)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ContactRequest import ContactRequest
from app.models.DoctorPatientAssignment import DoctorPatientAssignment


def get_contact_requests_for_doctor(
    db: Session,
    doctor_id: int,
    status: Optional[str] = None,
) -> List[ContactRequest]:
    """Retrieve active outreach task queue for doctor."""
    query = db.query(ContactRequest).filter(ContactRequest.doctor_id == doctor_id)
    if status:
        query = query.filter(ContactRequest.status == status)
    else:
        query = query.filter(ContactRequest.status.in_(["open", "in_progress"]))
    return query.order_by(ContactRequest.created_at.desc()).all()


def create_doctor_contact_request(
    db: Session,
    doctor_id: int = 1,
    patient_id: int = 1,
    message: str = "",
    urgency: Optional[str] = "routine",
    **kwargs
) -> ContactRequest:
    """Doctor-initiated contact task (F19c)."""
    req = ContactRequest(
        patient_id=patient_id,
        doctor_id=doctor_id,
        message=message,
        status="open",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_contact_request_by_id(db: Session, request_id: int) -> Optional[ContactRequest]:
    """Get single contact request."""
    return db.query(ContactRequest).filter(ContactRequest.id == request_id).first()


def update_contact_request_status(db: Session, request_id: int, new_status: str) -> ContactRequest:
    """Transition status ('open' -> 'in_progress')."""
    req = get_contact_request_by_id(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact request not found")

    req.status = new_status
    db.commit()
    db.refresh(req)
    return req


def complete_contact_request(db: Session, request_id: int, outcome_review_id: Optional[int] = None) -> ContactRequest:
    """Resolve contact task and link to resulting CaseReview."""
    req = get_contact_request_by_id(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact request not found")

    req.status = "responded"
    req.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return req


def get_all_contact_requests(db: Session, skip: int = 0, limit: int = 100) -> List[ContactRequest]:
    """List all contact requests."""
    return db.query(ContactRequest).offset(skip).limit(limit).all()


def create_contact_request(db: Session, cr_in: Any) -> ContactRequest:
    """Helper create."""
    cr = ContactRequest(
        patient_id=cr_in.patient_id,
        doctor_id=getattr(cr_in, "doctor_id", 1),
        message=cr_in.message,
        status=getattr(cr_in, "status", "open"),
    )
    db.add(cr)
    db.commit()
    db.refresh(cr)
    return cr


def update_contact_request(db: Session, request_id: int, update_in: Any) -> Optional[ContactRequest]:
    """Update contact request."""
    req = get_contact_request_by_id(db, request_id)
    if not req:
        return None
    for field, val in update_in.dict(exclude_unset=True).items():
        setattr(req, field, val)
    db.commit()
    db.refresh(req)
    return req
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
