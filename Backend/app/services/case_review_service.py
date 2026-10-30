

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.CaseReview import CaseReview
from app.models.patientprofile import PatientProfile
from app.models.user import User
from app.schemas.case_review import CaseReviewCreate, CaseReviewUpdate, CaseReviewOut


def create_case_review(db: Session, review_in: CaseReviewCreate) -> Optional[CaseReview]:
    """Create a case review (status, note, optional alert acknowledgment/closure).
    Verifies the patient and reviewer exist."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == review_in.patient_id).first()
        )
        if not patient:
            return None
        reviewer = None
        if review_in.reviewer_id is not None:
            reviewer = db.query(User).filter(User.id == review_in.reviewer_id).first()
            if not reviewer:
                return None
        status = getattr(review_in, "status", None) or "draft"
        db_review = CaseReview(
            patient_id=review_in.patient_id,
            reviewer_id=review_in.reviewer_id,
            status=status,
            reviewed_at=getattr(review_in, "reviewed_at", None),
            summary=getattr(review_in, "summary", None),
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review
    except SQLAlchemyError:
        db.rollback()
        raise


def get_case_review_by_id(db: Session, review_id: int) -> Optional[CaseReview]:
    """Retrieve a case review by its primary key."""
    return db.query(CaseReview).filter(CaseReview.id == review_id).first()


def get_all_case_reviews(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """List case reviews with optional patient_id / status filters."""
    query = db.query(CaseReview)
    if patient_id is not None:
        query = query.filter(CaseReview.patient_id == patient_id)
    if status is not None:
        query = query.filter(CaseReview.status == status)
    return query.order_by(CaseReview.created_at.desc()).offset(skip).limit(limit).all()


def update_case_review(
    db: Session, review_id: int, review_in: CaseReviewUpdate
) -> Optional[CaseReview]:
    """Update a case review (status or note). Per spec, If-Match / version concurrency
    is enforced at the route layer; this service applies the field changes."""
    try:
        db_review = get_case_review_by_id(db, review_id)
        if not db_review:
            return None
        update_data = review_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_review, field, value)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review
    except SQLAlchemyError:
        db.rollback()
        raise


