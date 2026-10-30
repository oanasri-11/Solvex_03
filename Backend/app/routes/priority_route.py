"""Priority assessment routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Priority assessments are backend-computed and immutable; they are never exposed to
patients and never edited or deleted by clients. Access: doctors and admins only.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_active_user, get_current_admin, get_current_doctor
from app.models.user import User
from app.services.priority_service import (
    create_priority_assessment,
    get_priority_assessment_by_id,
    get_all_priority_assessments,
)
from app.schemas.priority import (
    PriorityAssessmentCreate,
    PriorityAssessmentUpdate,
    PriorityAssessmentOut,
)

router = APIRouter(prefix="/priorities", tags=["priorities"])


def _require_doctor_or_admin(current_user: User) -> None:
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )


@router.get("/", response_model=List[PriorityAssessmentOut])
def list_priority_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
):
    """List priority assessments (doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    return get_all_priority_assessments(
        db, skip=skip, limit=limit, patient_id=patient_id, level=level
    )


@router.get("/{assessment_id}", response_model=PriorityAssessmentOut)
def get_priority_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a priority assessment by ID (doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    assessment = get_priority_assessment_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Priority assessment not found"
        )
    return assessment


@router.post(
    "/",
    response_model=PriorityAssessmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_priority_assessment_route(
    assessment_in: PriorityAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Backend-only creation of a priority assessment (doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    assessment = create_priority_assessment(db, assessment_in)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient or assessor not found",
        )
    return assessment

