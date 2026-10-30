
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.notification_service import (
    get_notification_by_id,
    get_all_notifications,
    get_unread_count,
    update_notification,
    mark_notification_read,
    mark_all_read,
    delete_notification,
)

from app.schemas.notification import (
    NotificationUpdate,
    NotificationOut,
)

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# Helper: Check notification ownership
def _require_notification_owner(
    notification,
    current_user: User,
):
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another user's notification",
        )


# 1. List current user's notifications
@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    unread: Optional[bool] = Query(None),
    notification_type: Optional[str] = Query(None, alias="type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return get_all_notifications(
        db,
        skip=skip,
        limit=limit,
        user_id=current_user.id,# type: ignore
        unread=unread,
        type=notification_type,
    )


# 2. Get unread notification count
@router.get("/unread-count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    count = get_unread_count(
        db,
        user_id=current_user.id,# type: ignore
    )

    return {"unread_count": count}


# 3. Mark all current user's notifications as read
@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated_count = mark_all_read(
        db,
        user_id=current_user.id,# type: ignore
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": updated_count,
    }


# 4. Get notification by ID
@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    _require_notification_owner(notification, current_user)

    return notification


# 5. Mark one notification as read
@router.post(
    "/{notification_id}/read",
    response_model=NotificationOut,
)
def mark_notification_as_read_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    _require_notification_owner(notification, current_user)

    updated = mark_notification_read(
        db,
        notification_id,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return updated


# 6. Update notification (read status only)
@router.patch(
    "/{notification_id}",
    response_model=NotificationOut,
)
def update_notification_route(
    notification_id: int,
    notification_in: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    _require_notification_owner(notification, current_user)

    # Only is_read should be accepted by NotificationUpdate.
    updated = update_notification(
        db,
        notification_id,
        notification_in,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return updated


# 7. Delete (dismiss) own notification
@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = get_notification_by_id(
        db,
        notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    _require_notification_owner(notification, current_user)

    deleted = delete_notification(
        db,
        notification_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return None

