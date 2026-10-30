<<<<<<< HEAD


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
=======
"""Notification service with alert routing and SLA escalation (Section 19, SC2, SC2b, SC2c, RS-4)."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.Notification import Notification
from app.models.Alert import Alert
from app.models.BloodPressureReading import BloodPressureReading
from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.CoverageTarget import CoverageTarget
from app.models.doctorprofile import DoctorProfile
from app.models.user import User


def route_notification_for_reading(
    db: Session,
    reading: BloodPressureReading,
    alerts: List[Alert],
) -> None:
    """Route notification based on monitoring mode and alert severity (SC2, SC2b)."""
    if not alerts:
        return

    from app.services.monitoring_mode_service import get_current_monitoring_mode
    mode = get_current_monitoring_mode(db, reading.patient_id)

    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.patient_id == reading.patient_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).first()

    if not assignment:
        return

    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == assignment.doctor_id).first()
    if not doctor or not doctor.user_id:
        return

    for alert in alerts:
        # In telemonitoring: always notify doctor
        # In self-monitoring: notify doctor actively only if critical emergency reached
        should_notify = (mode == "telemonitoring") or (alert.tier == "critical_emergency")
        if should_notify:
            notif = Notification(
                user_id=doctor.user_id,
                type="alert",
                title=f"BP Alert: {alert.tier.replace('_', ' ').title()}",
                message=f"Patient #{reading.patient_id} recorded {reading.systolic}/{reading.diastolic} mmHg. {alert.message}",
                is_read=False,
            )
            db.add(notif)
            alert.lifecycle = "delivered"

    db.commit()


def check_and_escalate_alerts(db: Session, sla_hours: int = 2) -> List[Alert]:
    """SLA escalation (SC2c): escalate unacknowledged critical alerts past SLA."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=sla_hours)
    unack_critical = db.query(Alert).filter(
        Alert.tier == "critical_emergency",
        Alert.lifecycle.in_(["raised", "delivered"]),
        Alert.acknowledged_at.is_(None),
        Alert.created_at <= cutoff
    ).all()

    escalated = []
    for alert in unack_critical:
        # Find doctor assignment
        assignment = db.query(DoctorPatientAssignment).filter(
            DoctorPatientAssignment.patient_id == alert.patient_id,
            DoctorPatientAssignment.is_active == True  # noqa: E712
        ).first()

        backup_user_id = None
        if assignment:
            coverage = db.query(CoverageTarget).filter(CoverageTarget.doctor_id == assignment.doctor_id).first()
            if coverage and coverage.backup_doctor_id:
                backup_doc = db.query(DoctorProfile).filter(DoctorProfile.id == coverage.backup_doctor_id).first()
                if backup_doc:
                    backup_user_id = backup_doc.user_id

        alert.lifecycle = "escalated"
        alert.escalated_at = datetime.now(timezone.utc)
        alert.escalated_to_user_id = backup_user_id
        escalated.append(alert)

        if backup_user_id:
            notif = Notification(
                user_id=backup_user_id,
                type="escalation",
                title="ESCALATED BP ALERT (SLA Breach)",
                message=f"Critical alert #{alert.id} for patient #{alert.patient_id} unacknowledged. Re-routed to you as backup clinician.",
                is_read=False,
            )
            db.add(notif)

    db.commit()
    return escalated


def get_notifications_for_user(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> List[Notification]:
    """List notifications for user."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
<<<<<<< HEAD
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
=======
    """Return count of unread notifications."""
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False  # noqa: E712
    ).count()


def mark_notification_read(db: Session, notification_id: int, user_id: Optional[int] = None) -> Notification:
    """Mark single notification as read."""
    query = db.query(Notification).filter(Notification.id == notification_id)
    if user_id is not None:
        query = query.filter(Notification.user_id == user_id)
    notif = query.first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_read(db: Session, user_id: int) -> int:
    """Mark all notifications read for user."""
    now = datetime.now(timezone.utc)
    updated = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False  # noqa: E712
    ).update({"is_read": True, "read_at": now})
    db.commit()
    return updated


def dismiss_notification(db: Session, notification_id: int, user_id: Optional[int] = None) -> bool:
    """Dismiss notification."""
    query = db.query(Notification).filter(Notification.id == notification_id)
    if user_id is not None:
        query = query.filter(Notification.user_id == user_id)
    notif = query.first()
    if not notif:
        return False
    db.delete(notif)
    db.commit()
    return True


def create_notification(db: Session, notification_in: Any) -> Notification:
    """Helper create."""
    notif = Notification(
        user_id=notification_in.user_id,
        type=getattr(notification_in, "type", "info"),
        title=getattr(notification_in, "title", "Notification"),
        message=getattr(notification_in, "message", None),
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_notification_by_id(db: Session, notification_id: int) -> Optional[Notification]:
    """Get single notification."""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_all_notifications(db: Session, skip: int = 0, limit: int = 100) -> List[Notification]:
    """List notifications."""
    return db.query(Notification).offset(skip).limit(limit).all()


def update_notification(db: Session, notification_id: int, update_in: Any) -> Optional[Notification]:
    """Update notification."""
    notif = get_notification_by_id(db, notification_id)
    if not notif:
        return None
    for field, val in update_in.dict(exclude_unset=True).items():
        setattr(notif, field, val)
    db.commit()
    db.refresh(notif)
    return notif


def delete_notification(db: Session, notification_id: int) -> bool:
    """Delete notification."""
    notif = get_notification_by_id(db, notification_id)
    if not notif:
        return False
    db.delete(notif)
    db.commit()
    return True
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
