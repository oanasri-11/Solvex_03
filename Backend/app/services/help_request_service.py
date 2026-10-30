"""Help request service.

CRUD operations for the PatientHelpRequest model, following classic SQLAlchemy syntax.
A help request creates the linked contact request automatically. Idempotency is
enforced at the route layer (Idempotency-Key header). There is no PATCH or DELETE;
a request can be cancelled (withdrawn) while the contact request is still open.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.PatientHelpRequest import PatientHelpRequest
from app.models.patientprofile import PatientProfile
from app.schemas.help_request import (
    PatientHelpRequestCreate,
    PatientHelpRequestUpdate,
    PatientHelpRequestOut,
)


def create_patient_help_request(
    db: Session, request_in: PatientHelpRequestCreate
) -> PatientHelpRequest:
    """Submit a help request. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == request_in.patient_id).first()
        )
        if not patient:
            return None
        db_request = PatientHelpRequest(
            patient_id=request_in.patient_id,
            type=request_in.type,
            status=request_in.status,
            description=request_in.description,
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except SQLAlchemyError:
        db.rollback()
        raise


def get_patient_help_request_by_id(db: Session, request_id: int) -> Optional[PatientHelpRequest]:
    """Retrieve a help request by its primary key."""
    return (
        db.query(PatientHelpRequest).filter(PatientHelpRequest.id == request_id).first()
    )


def get_all_patient_help_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """List help requests with optional patient_id / status filters."""
    query = db.query(PatientHelpRequest)
    if patient_id is not None:
        query = query.filter(PatientHelpRequest.patient_id == patient_id)
    if status is not None:
        query = query.filter(PatientHelpRequest.status == status)
    return query.order_by(PatientHelpRequest.created_at.desc()).offset(skip).limit(limit).all()


def cancel_patient_help_request(db: Session, request_id: int) -> Optional[PatientHelpRequest]:
    """Withdraw a help request while the contact request is still open."""
    try:
        db_request = get_patient_help_request_by_id(db, request_id)
        if not db_request:
            return None
        if db_request.status in ("done", "canceled"):
            return None
        db_request.status = "canceled"
        db_request.resolved_at = datetime.utcnow()
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except SQLAlchemyError:
        db.rollback()
        raise


# Note: update/delete are intentionally omitted. Help requests have no PATCH or DELETE
# per the specification; cancellation is expressed as a status change.