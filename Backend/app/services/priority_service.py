"""Priority service.

Read operations for the PriorityAssessment model, following classic SQLAlchemy syntax.
Priority is backend-computed only and never exposed to patients. There is no client-side
POST/PATCH/DELETE; assessments are written by the system and treated as immutable
audit-style records.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.PriorityAssessment import PriorityAssessment
from app.models.patientprofile import PatientProfile
from app.models.user import User
from app.schemas.priority import (
    PriorityAssessmentCreate,
    PriorityAssessmentUpdate,
    PriorityAssessmentOut,
)


def create_priority_assessment(
    db: Session, assessment_in: PriorityAssessmentCreate
) -> Optional[PriorityAssessment]:
    """Backend-only creation of a priority assessment. Verifies patient and assessor."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == assessment_in.patient_id).first()
        )
        if not patient:
            return None
        if assessment_in.assessor_id is not None:
            assessor = db.query(User).filter(User.id == assessment_in.assessor_id).first()
            if not assessor:
                return None
        assessed_at = getattr(assessment_in, "assessed_at", None) or datetime.utcnow()
        db_assessment = PriorityAssessment(
            patient_id=assessment_in.patient_id,
            assessor_id=assessment_in.assessor_id,
            level=assessment_in.level,
            assessed_at=assessed_at,
            notes=getattr(assessment_in, "notes", None),
        )
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        return db_assessment
    except SQLAlchemyError:
        db.rollback()
        raise


def get_priority_assessment_by_id(
    db: Session, assessment_id: int
) -> Optional[PriorityAssessment]:
    """Retrieve a priority assessment by its primary key."""
    return (
        db.query(PriorityAssessment).filter(PriorityAssessment.id == assessment_id).first()
    )


def get_all_priority_assessments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    level: Optional[str] = None,
):
    """List priority assessments with optional patient_id / level filters."""
    query = db.query(PriorityAssessment)
    if patient_id is not None:
        query = query.filter(PriorityAssessment.patient_id == patient_id)
    if level is not None:
        query = query.filter(PriorityAssessment.level == level)
    return query.order_by(PriorityAssessment.assessed_at.desc()).offset(skip).limit(limit).all()


# Note: update/delete are intentionally omitted. Priority assessments are backend-computed
# and immutable; they are never exposed to patients and never edited or deleted.
