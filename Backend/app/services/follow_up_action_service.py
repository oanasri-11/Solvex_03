

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.FollowUpAction import FollowUpAction
from app.models.patientprofile import PatientProfile
from app.schemas.follow_up import (
    FollowUpActionCreate,
    FollowUpActionUpdate,
    FollowUpActionOut,
)


def create_follow_up_action(db: Session, action_in: FollowUpActionCreate) -> Optional[FollowUpAction]:
    """Record a follow-up action. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == action_in.patient_id).first()
        )
        if not patient:
            return None
        status = getattr(action_in, "status", None) or "pending"
        db_action = FollowUpAction(
            patient_id=action_in.patient_id,
            type=action_in.type,
            status=status,
            due_date=getattr(action_in, "due_date", None),
            completed_at=getattr(action_in, "completed_at", None),
            notes=getattr(action_in, "notes", None),
        )
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action
    except SQLAlchemyError:
        db.rollback()
        raise


def get_follow_up_action_by_id(db: Session, action_id: int) -> Optional[FollowUpAction]:
    """Retrieve a follow-up action by its primary key."""
    return db.query(FollowUpAction).filter(FollowUpAction.id == action_id).first()


def get_all_follow_up_actions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """List follow-up actions with optional patient_id / status filters."""
    query = db.query(FollowUpAction)
    if patient_id is not None:
        query = query.filter(FollowUpAction.patient_id == patient_id)
    if status is not None:
        query = query.filter(FollowUpAction.status == status)
    return query.order_by(FollowUpAction.id.desc()).offset(skip).limit(limit).all()


def update_follow_up_action(
    db: Session, action_id: int, action_in: FollowUpActionUpdate
) -> Optional[FollowUpAction]:
    """Update a follow-up action."""
    try:
        db_action = get_follow_up_action_by_id(db, action_id)
        if not db_action:
            return None
        update_data = action_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_action, field, value)
        if db_action.status == "completed" and db_action.completed_at is None:# type: ignore
            db_action.completed_at = datetime.utcnow()# type: ignore
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action
    except SQLAlchemyError:
        db.rollback()
        raise




def complete_follow_up_action(db: Session, action_id: int) -> Optional[FollowUpAction]:
    """Mark a follow-up action as completed (soft delete).
    
    This function is an alias for delete_follow_up_action, renamed to better
    reflect its actual behavior: moving the action to a completed state.
    """
    return delete_follow_up_action(db, action_id)
def delete_follow_up_action(db: Session, action_id: int) -> Optional[FollowUpAction]:
    """Soft delete a follow-up action only if it is not completed.

    The model carries no is_active field, so the soft delete is expressed by moving
    the action to a terminal (completed) state with a completed_at timestamp when it
    is not already completed. Completed actions cannot be removed.
    """
    try:
        db_action = get_follow_up_action_by_id(db, action_id)
        if not db_action:
            return None
        if db_action.status == "completed":# type: ignore
            return None
        db_action.status = "completed"# type: ignore
        db_action.completed_at = datetime.utcnow()# type: ignore
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action
    except SQLAlchemyError:
        db.rollback()
        raise
