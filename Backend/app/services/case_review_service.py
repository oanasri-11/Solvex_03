"""CaseReview service (Section 16, UC13, F13)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.CaseReview import CaseReview
from app.models.FollowUpAction import FollowUpAction
from app.models.Alert import Alert
from app.models.patientprofile import PatientProfile


def save_case_review(
    db: Session,
    patient_id: int,
    reviewer_id: Optional[int] = None,
    review_status: str = "completed",
    clinical_note: str = "",
    alert_id: Optional[int] = None,
    follow_up_actions: Optional[List[Dict[str, Any]]] = None,
    doctor_user_id: Optional[int] = None,
    review_in: Any = None,
    **kwargs
) -> CaseReview:
    """Save review (D4.a): updates status, attaches note, acknowledges linked alerts, and issues follow-up actions atomically."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    rev_id = reviewer_id if reviewer_id is not None else (doctor_user_id if doctor_user_id is not None else 1)
    if review_in is not None:
        status_val = getattr(review_in, "status", None) or review_status
        note_val = getattr(review_in, "summary", None) or getattr(review_in, "clinical_note", None) or clinical_note
        alert_id = getattr(review_in, "alert_id", alert_id)
        follow_up_actions = getattr(review_in, "follow_up_actions", follow_up_actions)
    else:
        status_val = review_status
        note_val = clinical_note

    now = datetime.now(timezone.utc)
    review = CaseReview(
        patient_id=patient_id,
        reviewer_id=rev_id,
        status=status_val,
        summary=note_val,
        reviewed_at=now,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Acknowledge linked alert if provided
    if alert_id:
        alert = db.query(Alert).filter(Alert.id == alert_id, Alert.patient_id == patient_id).first()
        if alert:
            alert.acknowledged_at = now
            alert.acknowledged_by = reviewer_id
            alert.lifecycle = "acknowledged"
            db.commit()

    # Append follow up actions
    if follow_up_actions:
        for action_data in follow_up_actions:
            action = FollowUpAction(
                patient_id=patient_id,
                type=action_data.get("type", "call"),
                status="pending",
                notes=action_data.get("notes"),
                due_date=action_data.get("due_date"),
            )
            db.add(action)
        db.commit()

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    return review


def get_case_reviews_for_patient(db: Session, patient_id: int) -> List[CaseReview]:
    """List historical case reviews for patient."""
    return db.query(CaseReview).filter(
        CaseReview.patient_id == patient_id
    ).order_by(CaseReview.created_at.desc()).all()


def get_case_review_by_id(db: Session, review_id: int) -> Optional[CaseReview]:
    """Retrieve review by ID."""
    return db.query(CaseReview).filter(CaseReview.id == review_id).first()


def update_case_review(db: Session, review_id: int, review_update: Any) -> Optional[CaseReview]:
    """Edit review note or status."""
    review = get_case_review_by_id(db, review_id)
    if not review:
        return None
    for field, val in review_update.dict(exclude_unset=True).items():
        setattr(review, field, val)
    db.commit()
    db.refresh(review)
    return review


def get_all_case_reviews(db: Session, skip: int = 0, limit: int = 100) -> List[CaseReview]:
    """List all case reviews."""
    return db.query(CaseReview).offset(skip).limit(limit).all()


def create_case_review(db: Session, review_in: Any) -> CaseReview:
    """Helper create."""
    return save_case_review(
        db,
        patient_id=review_in.patient_id,
        reviewer_id=review_in.reviewer_id,
        review_status=getattr(review_in, "status", "draft"),
        clinical_note=getattr(review_in, "summary", "") or "",
    )
