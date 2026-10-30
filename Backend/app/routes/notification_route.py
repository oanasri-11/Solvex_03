"""Notifications API routes (Section 19)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.services.notification_service import (
    get_notifications_for_user,
    get_unread_count,
    get_notification_by_id,
    mark_notification_read,
    mark_all_read,
    dismiss_notification,
)
from app.schemas.notification import (
    NotificationOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationOut])
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
):
    """Notification list for current authenticated user."""
    return get_notifications_for_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )


@router.get("/unread-count")
def get_user_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Unread counter for bell badge."""
    count = get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.get("/{id}", response_model=NotificationOut)
def get_single_notification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Single notification details."""
    notification = get_notification_by_id(db, id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.patch("/{id}/read", response_model=NotificationOut)
def mark_single_notification_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark notification as read."""
    notification = get_notification_by_id(db, id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return mark_notification_read(db, id)


@router.post("/read-all", response_model=MessageResponse)
def bulk_mark_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Bulk mark read."""
    mark_all_read(db, current_user.id)
    return MessageResponse(message="All notifications marked as read")


@router.delete("/{id}", response_model=MessageResponse)
def dismiss_single_notification(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Dismiss notification."""
    notification = get_notification_by_id(db, id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    dismiss_notification(db, id)
    return MessageResponse(message=f"Notification {id} dismissed")
