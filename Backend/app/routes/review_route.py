"""CaseReview & FollowUpAction API routes (Section 16)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.case_review_service import (
    save_case_review,
    get_case_reviews_for_patient,
    get_case_review_by_id,
    update_case_review,
)
from app.services.follow_up_action_service import (
    create_follow_up_action,
    get_follow_up_actions_for_patient,
    get_follow_up_action_by_id,
    update_follow_up_action,
    delete_follow_up_action,
)
from app.schemas.case_review import (
    CaseReviewCreate,
    CaseReviewUpdate,
    CaseReviewOut,
)
from app.schemas.follow_up import (
    FollowUpActionCreate,
    FollowUpActionUpdate,
    FollowUpActionOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["reviews"])


# ==========================================
# Case Reviews
# ==========================================

@router.post(
    "/doctor/patients/{id}/reviews",
    response_model=CaseReviewOut,
    status_code=status.HTTP_201_CREATED,
)
def doctor_save_review(
    id: int,
    review_in: CaseReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Save review (D4.a): status, note, acknowledges alerts, issues follow-ups in one atomic transaction."""
    check_patient_access(current_user, id, db)
    return save_case_review(
        db,
        patient_id=id,
        doctor_user_id=current_user.id,
        review_in=review_in,
    )


@router.get("/doctor/patients/{id}/reviews", response_model=List[CaseReviewOut])
def doctor_get_patient_reviews(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Historical clinical review log for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_case_reviews_for_patient(db, id)


@router.get("/reviews/{id}", response_model=CaseReviewOut)
def get_review_by_id_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Single review detail."""
    review = get_case_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    check_patient_access(current_user, review.patient_id, db)
    return review


@router.patch("/reviews/{id}", response_model=CaseReviewOut)
def update_review_route(
    id: int,
    review_in: CaseReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    if_match: Optional[str] = Header(None, alias="If-Match"),
):
    """Edit note or status (If-Match version check)."""
    review = get_case_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    check_patient_access(current_user, review.patient_id, db)

    # Concurrency check
    if if_match and hasattr(review, "version") and str(review.version) != if_match.strip('"'):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CONCURRENT_UPDATE")

    return update_case_review(db, id, review_in)


# ==========================================
# Follow-Up Actions
# ==========================================

@router.post(
    "/reviews/{id}/follow-up-actions",
    response_model=FollowUpActionOut,
    status_code=status.HTTP_201_CREATED,
)
def append_follow_up_action(
    id: int,
    action_in: FollowUpActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Append follow-up task to a review."""
    review = get_case_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    check_patient_access(current_user, review.patient_id, db)

    action_in.patient_id = review.patient_id
    return create_follow_up_action(db, action_in)


@router.get("/doctor/patients/{id}/follow-up-actions", response_model=List[FollowUpActionOut])
def get_patient_follow_up_actions(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Active follow-up task list for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_follow_up_actions_for_patient(db, id)


@router.patch("/follow-up-actions/{id}", response_model=FollowUpActionOut)
def update_follow_up_action_route(
    id: int,
    action_in: FollowUpActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Complete or update a follow-up task."""
    action = get_follow_up_action_by_id(db, id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow-up action not found")
    check_patient_access(current_user, action.patient_id, db)
    return update_follow_up_action(db, id, action_in)


@router.delete("/follow-up-actions/{id}", response_model=MessageResponse)
def delete_follow_up_action_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Soft-delete incomplete action."""
    action = get_follow_up_action_by_id(db, id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow-up action not found")
    check_patient_access(current_user, action.patient_id, db)
    delete_follow_up_action(db, id)
    return MessageResponse(message=f"Follow-up action {id} deleted")
