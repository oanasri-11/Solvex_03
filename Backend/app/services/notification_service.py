

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.Notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationOut,
)


def create_notification(db: Session, notification_in: NotificationCreate) -> Optional[Notification]:
    """System-only creation of a notification. Verifies the user exists."""
    try:
        user = db.query(User).filter(User.id == notification_in.user_id).first()
        if not user:
            return None
        is_read_val = getattr(notification_in, "is_read", False)
        if is_read_val is None:
            is_read_val = False
        db_notification = Notification(
            user_id=notification_in.user_id,
            type=notification_in.type,
            title=notification_in.title,
            message=getattr(notification_in, "message", None),
            is_read=is_read_val,
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError:
        db.rollback()
        raise


def get_notification_by_id(db: Session, notification_id: int) -> Optional[Notification]:
    """Retrieve a notification by its primary key."""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_all_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    unread: Optional[bool] = None,
    type: Optional[str] = None,
):
    """List notifications with optional user_id / unread / type filters."""
    query = db.query(Notification)
    if user_id is not None:
        query = query.filter(Notification.user_id == user_id)
    if unread is not None:
        if unread:
            query = query.filter(Notification.is_read == False)  # noqa: E712
        else:
            query = query.filter(Notification.is_read == True)  # noqa: E712
    if type is not None:
        query = query.filter(Notification.type == type)
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
    """Return the unread notification count for a user (bell badge)."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .count()
    )


def update_notification(
    db: Session, notification_id: int, notification_in: NotificationUpdate
) -> Optional[Notification]:
    """Update a notification (used to mark read)."""
    try:
        db_notification = get_notification_by_id(db, notification_id)
        if not db_notification:
            return None
        update_data = notification_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_notification, field, value)
        if update_data.get("is_read") is True and db_notification.read_at is None:
            db_notification.read_at = datetime.utcnow()# type: ignore
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError:
        db.rollback()
        raise


def mark_notification_read(db: Session, notification_id: int) -> Optional[Notification]:
    """Mark a notification as read."""
    try:
        db_notification = get_notification_by_id(db, notification_id)
        if not db_notification:
            return None
        db_notification.is_read = True# type: ignore
        db_notification.read_at = datetime.utcnow()# type: ignore
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError:
        db.rollback()
        raise


def mark_all_read(db: Session, user_id: int) -> int:
    """Mark all notifications of a user as read. Returns the number updated."""
    try:
        unread_notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .all()
        )
        now = datetime.utcnow()
        for item in unread_notifications:
            item.is_read = True# type: ignore
            item.read_at = now# type: ignore
        db.commit()
        return len(unread_notifications)
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_notification(db: Session, notification_id: int) -> bool:
    """Dismiss (delete) an own notification. Notifications are convenience records."""
    try:
        db_notification = get_notification_by_id(db, notification_id)
        if not db_notification:
            return False
        db.delete(db_notification)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        raise
