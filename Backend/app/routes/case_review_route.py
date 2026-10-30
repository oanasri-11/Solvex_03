<<<<<<< HEAD
"""Case review routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Case reviews are an audit trail: no DELETE. Access control:
- patients only their own reviews; doctors only assigned patients; admins full.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.patient_service import get_patient_profile_by_user_id
from app.services.case_review_service import (
    create_case_review,
    get_case_review_by_id,
    get_all_case_reviews,
    update_case_review,
)
from app.schemas.case_review import (
    CaseReviewCreate,
    CaseReviewUpdate,
    CaseReviewOut,
)

router = APIRouter(prefix="/case-reviews", tags=["case-reviews"])


def _patient_profile_for(db: Session, current_user: User):
    if current_user.role == "patient": # type: ignore
        return get_patient_profile_by_user_id(db, current_user.id) # type: ignore
    return None


def _require_review_access(current_user: User, review, db: Session) -> None:
    if current_user.role == "patient": # type: ignore
        check_patient_access(current_user, review.patient_id, db)
    elif current_user.role == "doctor": # type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import is_doctor_assigned

        if not is_doctor_assigned(db, current_user.doctor_profile.id, review.patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )


@router.get("/", response_model=List[CaseReviewOut])
def list_case_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
):
    """List case reviews."""
    reviews = get_all_case_reviews(
        db, skip=skip, limit=limit, patient_id=patient_id, status=status
    )
    if current_user.role == "patient": # type: ignore
        profile = _patient_profile_for(db, current_user)
        if not profile:
            return []
        reviews = [r for r in reviews if r.patient_id == profile.id] # type: ignore
    elif current_user.role == "doctor": # type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found" # type: ignore
            )
        from app.services.assignment_service import get_all_assignments

        assignments = get_all_assignments(
            db, doctor_id=current_user.doctor_profile.id, active=True
        )
        allowed_patient_ids = {a.patient_id for a in assignments}
        reviews = [r for r in reviews if r.patient_id in allowed_patient_ids]
    return reviews


@router.get("/{review_id}", response_model=CaseReviewOut)
def get_case_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a case review by ID."""
    review = get_case_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case review not found"
        )
    _require_review_access(current_user, review, db)
    return review


@router.post(
    "/",
    response_model=CaseReviewOut,
    status_code=status.HTTP_201_CREATED,
)
def create_case_review_route(
    review_in: CaseReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a case review."""
    if current_user.role == "patient": # type: ignore
        profile = _patient_profile_for(db, current_user)
        if not profile or review_in.patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients may only create reviews for themselves",
            )
    review = create_case_review(db, review_in)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient or reviewer not found",
        )
    return review


@router.put("/{review_id}", response_model=CaseReviewOut)
def update_case_review_route(
    review_id: int,
    review_in: CaseReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a case review."""
    review = get_case_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case review not found"
        )
    _require_review_access(current_user, review, db)
    updated = update_case_review(db, review_id, review_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case review not found"
        )
    return updated

=======
"""CaseReview API routes (Section 16 alias)."""

from app.routes.review_route import router

__all__ = ["router"]
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
