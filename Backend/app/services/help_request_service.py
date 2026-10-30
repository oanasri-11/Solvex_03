<<<<<<< HEAD


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
) -> Optional[PatientHelpRequest]:
    """Submit a help request. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == request_in.patient_id).first()
        )
        if not patient:
            return None
        status = getattr(request_in, "status", None) or "open"
        db_request = PatientHelpRequest(
            patient_id=request_in.patient_id,
            type=request_in.type,
            status=status,
            description=getattr(request_in, "description", None),
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
        if db_request.status in ("done", "canceled", "resolved", "closed"):
            return None
        db_request.status = "canceled"# type: ignore
        db_request.resolved_at = datetime.utcnow()# type: ignore
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except SQLAlchemyError:
        db.rollback()
        raise


# 
=======
"""PatientHelpRequest service (Section 17, UC17, F17, UC19a)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.PatientHelpRequest import PatientHelpRequest
from app.models.ContactRequest import ContactRequest
from app.models.patientprofile import PatientProfile
from app.models.DoctorPatientAssignment import DoctorPatientAssignment


def create_patient_help_request(
    db: Session,
    patient_id: int,
    urgency: str = "general",
    message: str = "",
    attached_reading_id: Optional[int] = None,
    acknowledged_not_emergency: bool = True,
    request_in: Any = None,
    actor_user_id: Optional[int] = None,
) -> PatientHelpRequest:
    if request_in is not None:
        urgency = getattr(request_in, "urgency", None) or getattr(request_in, "type", None) or urgency
        message = getattr(request_in, "message", None) or getattr(request_in, "description", None) or message
        attached_reading_id = getattr(request_in, "attached_reading_id", attached_reading_id)
        if hasattr(request_in, "acknowledged_not_emergency"):
            acknowledged_not_emergency = request_in.acknowledged_not_emergency
    """Submit help request (F17); automatically creates linked ContactRequest (UC19a)."""
    if not acknowledged_not_emergency:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="EMERGENCY_GUIDANCE_REQUIRED: You must confirm this is not a medical emergency before submitting a routine help request"
        )

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    # Find assigned doctor
    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).first()
    doctor_id = assignment.doctor_id if assignment else None

    # 1. Create HelpRequest
    help_req = PatientHelpRequest(
        patient_id=patient_id,
        type=urgency,
        description=message,
        status="open",
    )
    db.add(help_req)
    db.commit()
    db.refresh(help_req)

    # 2. Automatically generate linked ContactRequest (UC19a)
    contact_req = ContactRequest(
        patient_id=patient_id,
        doctor_id=doctor_id or 1,
        message=f"[Help Request: {urgency}] {message}",
        status="open",
    )
    db.add(contact_req)
    db.commit()
    db.refresh(contact_req)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    return help_req


def get_patient_help_requests(db: Session, patient_id: int) -> List[PatientHelpRequest]:
    """List help requests for patient."""
    return db.query(PatientHelpRequest).filter(
        PatientHelpRequest.patient_id == patient_id
    ).order_by(PatientHelpRequest.created_at.desc()).all()


def get_patient_help_request_by_id(db: Session, request_id: int) -> Optional[PatientHelpRequest]:
    """Get single help request."""
    return db.query(PatientHelpRequest).filter(PatientHelpRequest.id == request_id).first()


def cancel_patient_help_request(db: Session, request_id: int, patient_id: Optional[int] = None) -> PatientHelpRequest:
    """Cancel pending help request before clinician pickup."""
    req = get_patient_help_request_by_id(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Help request not found")

    if patient_id and req.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if req.status != "open":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot cancel request already picked up")

    req.status = "closed"
    req.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, req.patient_id)
    except Exception:
        pass

    return req


def get_all_patient_help_requests(db: Session, skip: int = 0, limit: int = 100) -> List[PatientHelpRequest]:
    """List all help requests."""
    return db.query(PatientHelpRequest).offset(skip).limit(limit).all()
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
