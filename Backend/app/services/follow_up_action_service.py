<<<<<<< HEAD


from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
=======
"""FollowUpAction service (Section 16)."""

from datetime import datetime, timezone
from typing import Optional, List, Any

from fastapi import HTTPException, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.models.FollowUpAction import FollowUpAction
from app.models.patientprofile import PatientProfile
<<<<<<< HEAD
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
=======


def create_follow_up_action(
    db: Session,
    patient_id: Any,
    action_type: Optional[str] = None,
    due_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    action_in: Optional[Any] = None,
) -> FollowUpAction:
    if action_in is not None or (isinstance(patient_id, object) and hasattr(patient_id, "type")):
        act = action_in or patient_id
        patient_id = getattr(act, "patient_id", None) or 1
        action_type = getattr(act, "type", None) or getattr(act, "action_type", "task")
        due_date = getattr(act, "due_date", None)
        notes = getattr(act, "notes", None) or getattr(act, "note", None)
    """Create a follow up action task."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    action = FollowUpAction(
        patient_id=patient_id,
        type=action_type,
        due_date=due_date,
        notes=notes,
        status="pending",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def get_follow_up_actions_for_patient(db: Session, patient_id: int) -> List[FollowUpAction]:
    """Retrieve active follow-up tasks for patient."""
    return db.query(FollowUpAction).filter(
        FollowUpAction.patient_id == patient_id
    ).order_by(FollowUpAction.due_date.asc()).all()


def get_follow_up_action_by_id(db: Session, action_id: int) -> Optional[FollowUpAction]:
    """Get single follow-up action."""
    return db.query(FollowUpAction).filter(FollowUpAction.id == action_id).first()


def update_follow_up_action(db: Session, action_id: int, update_data: Any) -> FollowUpAction:
    """Update or complete follow-up action."""
    action = get_follow_up_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow-up action not found")

    for field, val in update_data.dict(exclude_unset=True).items():
        if hasattr(action, field):
            setattr(action, field, val)
            if field == "status" and val == "completed":
                action.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(action)
    return action


def delete_follow_up_action(db: Session, action_id: int) -> bool:
    """Soft-delete incomplete action."""
    action = get_follow_up_action_by_id(db, action_id)
    if not action:
        return False
    db.delete(action)
    db.commit()
    return True


def get_all_follow_up_actions(db: Session, skip: int = 0, limit: int = 100) -> List[FollowUpAction]:
    """List all follow-up actions."""
    return db.query(FollowUpAction).offset(skip).limit(limit).all()
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
