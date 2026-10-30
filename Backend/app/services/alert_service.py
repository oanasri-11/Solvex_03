"""Alert service.

Read operations for the Alert model, following classic SQLAlchemy syntax.
Alerts are created only by the backend and never deleted. Lifecycle only moves forward
(raised -> delivered -> acknowledged -> closed). Acknowledge and close recalculate
priority (handled by the calling service/route layer).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.Alert import Alert
from app.models.PatientProfile import PatientProfile# type: ignore
from app.schemas.alert import AlertCreate, AlertUpdate, AlertOut


def create_alert(db: Session, alert_in: AlertCreate) -> Optional[Alert]:
    """Backend-only creation of an alert record. Verifies the patient exists."""
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == alert_in.patient_id).first()
        )
        if not patient:
            return None
        status = getattr(alert_in, "status", None) or "new"
        db_alert = Alert(
            patient_id=alert_in.patient_id,
            alert_type=alert_in.alert_type,
            severity=alert_in.severity,
            status=status,
            message=getattr(alert_in, "message", None),
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    except SQLAlchemyError:
        db.rollback()
        raise


def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
    """Retrieve an alert by its primary key."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_all_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    lifecycle: Optional[str] = None,
    severity_level: Optional[str] = None,
):
    """List alerts with optional patient_id / lifecycle / severity filters."""
    query = db.query(Alert)
    if patient_id is not None:
        query = query.filter(Alert.patient_id == patient_id)
    if lifecycle is not None:
        query = query.filter(Alert.status == lifecycle)
    if severity_level is not None:
        query = query.filter(Alert.severity == severity_level)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def update_alert(db: Session, alert_id: int, alert_in: AlertUpdate) -> Optional[Alert]:
    """Update an alert (used for acknowledge / close lifecycle transitions)."""
    try:
        db_alert = get_alert_by_id(db, alert_id)
        if not db_alert:
            return None
        update_data = alert_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_alert, field, value)
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    except SQLAlchemyError:
        db.rollback()
        raise


def acknowledge_alert(db: Session, alert_id: int, acknowledged_by: int) -> Optional[Alert]:
    """Acknowledge an alert (lifecycle moves forward)."""
    try:
        db_alert = get_alert_by_id(db, alert_id)
        if not db_alert:
            return None
        if db_alert.status not in ("raised", "delivered", "new", "open"):
            return None
        db_alert.status = "acknowledged"# type: ignore
        db_alert.acknowledged_at = datetime.utcnow()# type: ignore
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    except SQLAlchemyError:
        db.rollback()
        raise


def close_alert(db: Session, alert_id: int, closed_by: int) -> Optional[Alert]:
    """Close an alert (lifecycle moves forward)."""
    try:
        db_alert = get_alert_by_id(db, alert_id)
        if not db_alert:
            return None
        if db_alert.status not in ("raised", "delivered", "acknowledged", "new", "open"):
            return None
        db_alert.status = "closed"# type: ignore
        db_alert.resolved_at = datetime.utcnow()# type: ignore
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    except SQLAlchemyError:
        db.rollback()
        raise


# Note: delete is intentionally omitted. Alerts are never deleted per the specification.
