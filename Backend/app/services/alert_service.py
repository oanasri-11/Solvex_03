<<<<<<< HEAD


from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.Alert import Alert
from app.models.PatientProfile import PatientProfile# type: ignore
from app.schemas.alert import AlertCreate, AlertUpdate, AlertOut


def create_alert(db: Session, alert_in: AlertCreate) -> Optional[Alert]:
    """Backend-only creation of an alert record. Verifies the patient exists."""
=======
"""Alert service managing clinical alert generation, acknowledgment (SC3), and evidence packets."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.Alert import Alert
from app.models.AlertReading import AlertReading
from app.models.patientprofile import PatientProfile
from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.schemas.alert import AlertCreate, AlertUpdate


def create_alert(db: Session, alert_in: AlertCreate) -> Optional[Alert]:
    """Backend-only creation of an alert record."""
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    try:
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == alert_in.patient_id).first()
        )
        if not patient:
            return None
<<<<<<< HEAD
        status = getattr(alert_in, "status", None) or "new"
=======
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
        db_alert = Alert(
            patient_id=alert_in.patient_id,
            alert_type=alert_in.alert_type,
            severity=alert_in.severity,
<<<<<<< HEAD
            status=status,
=======
            tier=getattr(alert_in, "tier", "routine_out_of_range") or "routine_out_of_range",
            trigger_type=getattr(alert_in, "trigger_type", "single_reading") or "single_reading",
            status=getattr(alert_in, "status", "new") or "new",
            lifecycle=getattr(alert_in, "lifecycle", "raised") or "raised",
            rule_version_id=getattr(alert_in, "rule_version_id", None),
            justification=getattr(alert_in, "justification", None),
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
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
<<<<<<< HEAD
):
    """List alerts with optional patient_id / lifecycle / severity filters."""
=======
    tier: Optional[str] = None,
) -> List[Alert]:
    """List alerts with optional filters."""
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    query = db.query(Alert)
    if patient_id is not None:
        query = query.filter(Alert.patient_id == patient_id)
    if lifecycle is not None:
<<<<<<< HEAD
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
=======
        query = query.filter(Alert.lifecycle == lifecycle)
    if severity_level is not None:
        query = query.filter(Alert.severity == severity_level)
    if tier is not None:
        query = query.filter(Alert.tier == tier)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def get_alerts_for_doctor(
    db: Session,
    doctor_id: int,
    tier: Optional[str] = None,
    lifecycle: Optional[str] = None,
    unacknowledged: Optional[bool] = None,
    unacknowledged_only: Optional[bool] = None,
) -> List[Alert]:
    if unacknowledged_only is not None and unacknowledged is None:
        unacknowledged = unacknowledged_only
    """List alerts across assigned patients."""
    assigned_patients = db.query(DoctorPatientAssignment.patient_id).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).all()
    patient_ids = [p[0] for p in assigned_patients]
    if not patient_ids:
        return []

    query = db.query(Alert).filter(Alert.patient_id.in_(patient_ids))
    if tier:
        query = query.filter(Alert.tier == tier)
    if lifecycle:
        query = query.filter(Alert.lifecycle == lifecycle)
    if unacknowledged is True:
        query = query.filter(Alert.acknowledged_at.is_(None))

    return query.order_by(Alert.created_at.desc()).all()


def get_alerts_for_patient(db: Session, patient_id: int, active_only: bool = True) -> List[Alert]:
    """List active patient-facing alerts."""
    query = db.query(Alert).filter(Alert.patient_id == patient_id)
    if active_only:
        query = query.filter(Alert.lifecycle.in_(["raised", "delivered", "escalated"]))
    return query.order_by(Alert.created_at.desc()).all()


def get_alert_evidence(db: Session, alert_id: int) -> Dict[str, Any]:
    """Full evidence packet: triggering reading IDs, baseline window, active RuleVersion ID, escalation history."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert_readings = db.query(AlertReading).filter(AlertReading.alert_id == alert_id).all()
    reading_ids = [ar.reading_id for ar in alert_readings]

    from app.models.BloodPressureReading import BloodPressureReading
    readings = db.query(BloodPressureReading).filter(BloodPressureReading.id.in_(reading_ids)).all() if reading_ids else []

    return {
        "alert": alert,
        "triggering_readings": readings,
        "justification": alert.justification,
        "rule_version_id": alert.rule_version_id,
        "escalation_history": {
            "escalated_at": alert.escalated_at.isoformat() if alert.escalated_at else None,
            "escalated_to_user_id": alert.escalated_to_user_id,
        },
        "lifecycle": alert.lifecycle,
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
    }


def acknowledge_alert(db: Session, alert_id: int, doctor_user_id: int) -> Alert:
    """Doctor acknowledges receipt (stops SLA escalation timer; SC3). Recalculates priority."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = doctor_user_id
    alert.lifecycle = "acknowledged"
    alert.status = "acknowledged"
    db.commit()
    db.refresh(alert)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, alert.patient_id)
    except Exception:
        pass

    return alert


def close_alert(
    db: Session,
    alert_id: int,
    doctor_user_id: int,
    note: Optional[str] = None,
    clinical_note: Optional[str] = None,
) -> Alert:
    if clinical_note:
        note = clinical_note
    """Resolve/close an alert following clinical action."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    now = datetime.now(timezone.utc)
    alert.closed_at = now
    alert.closed_by = doctor_user_id
    alert.resolved_at = now
    alert.lifecycle = "closed"
    alert.status = "resolved"
    db.commit()
    db.refresh(alert)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, alert.patient_id)
    except Exception:
        pass

    return alert


def patient_acknowledge_alert(db: Session, alert_id: int, patient_user_id: int) -> Alert:
    """Patient confirms reading emergency guidance (UC09b / RS-1)."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.patient_acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def update_alert(db: Session, alert_id: int, alert_in: AlertUpdate) -> Optional[Alert]:
    """Update alert fields."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    for field, value in alert_in.dict(exclude_unset=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
