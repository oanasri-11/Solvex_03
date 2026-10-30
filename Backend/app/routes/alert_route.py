<<<<<<< HEAD
"""Alert routes: CRUD for Alert model."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
=======
"""Alert & AlertReading API routes (Section 12)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
<<<<<<< HEAD
    get_current_admin,
    get_current_patient,
)
from app.models.user import User
from app.services.alert_service import (
    create_alert,
    get_alert_by_id,
    get_all_alerts,
    update_alert,
    acknowledge_alert,
    close_alert,
)
from app.models.Alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    """List alerts with optional filters."""
    return get_all_alerts(
        db, skip=skip, limit=limit,
        patient_id=patient_id, lifecycle=status, severity_level=severity,
    )


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get an alert by ID."""
    db_alert = get_alert_by_id(db, alert_id)
    if not db_alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return db_alert


@router.post("/", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert_route(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an alert."""
    db_alert = create_alert(db, alert_in)
    if not db_alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return db_alert


@router.put("/{alert_id}", response_model=AlertOut)
def update_alert_route(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an alert (acknowledge/close lifecycle)."""
    db_alert = update_alert(db, alert_id, alert_in)
    if not db_alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return db_alert


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert_route(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Acknowledge an alert."""
    db_alert = acknowledge_alert(db, alert_id, current_user.id)#type:ignore
    if not db_alert:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alert cannot be acknowledged")
    return db_alert


@router.post("/{alert_id}/close", response_model=AlertOut)
def close_alert_route(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Close an alert."""
    db_alert = close_alert(db, alert_id, current_user.id) # type: ignore
    if not db_alert:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alert cannot be closed")
    return db_alert
=======
    get_current_patient,
    get_current_caregiver_or_patient,
    check_patient_access,
    resolve_acting_patient_id,
)
from app.models.user import User
from app.services.alert_service import (
    get_alerts_for_patient,
    get_alerts_for_doctor,
    get_alert_by_id,
    get_alert_evidence,
    acknowledge_alert,
    close_alert,
    patient_acknowledge_alert,
)
from app.schemas.alert import (
    AlertOut,
    AlertAcknowledgeRequest,
    AlertCloseRequest,
    AlertPatientAcknowledgeRequest,
)

router = APIRouter(tags=["alerts"])


@router.get("/patients/me/alerts", response_model=List[AlertOut])
def get_own_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Active patient-facing safety alerts with plain-language guidance."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_alerts_for_patient(db, current_user.patient_profile.id, active_only=True)


@router.get("/doctor/me/alerts", response_model=List[AlertOut])
def get_doctor_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    tier: Optional[str] = Query(None),
    lifecycle: Optional[str] = Query(None),
    unacknowledged: Optional[bool] = Query(None),
):
    """Alerts across assigned patients (filters: tier, lifecycle, unacknowledged)."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return get_alerts_for_doctor(
        db,
        doctor_id=current_user.doctor_profile.id,
        tier=tier,
        lifecycle=lifecycle,
        unacknowledged_only=unacknowledged,
    )


@router.get("/doctor/patients/{id}/alerts", response_model=List[AlertOut])
def get_patient_alerts(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Alert history for a specific patient."""
    check_patient_access(current_user, id, db)
    return get_alerts_for_patient(db, id, active_only=False)


@router.get("/alerts/{id}")
def get_alert_evidence_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Full evidence packet: triggering reading IDs, baseline window, active RuleVersion, escalation history."""
    alert = get_alert_by_id(db, id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    check_patient_access(current_user, alert.patient_id, db)
    evidence = get_alert_evidence(db, id)
    return evidence or alert


@router.post("/alerts/{id}/acknowledge", response_model=AlertOut)
def acknowledge_alert_route(
    id: int,
    ack_in: AlertAcknowledgeRequest = AlertAcknowledgeRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Doctor acknowledges receipt (stops SLA escalation timer; SC3)."""
    alert = get_alert_by_id(db, id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    check_patient_access(current_user, alert.patient_id, db)
    return acknowledge_alert(db, id, doctor_user_id=current_user.id)


@router.post("/alerts/{id}/close", response_model=AlertOut)
def close_alert_route(
    id: int,
    close_in: AlertCloseRequest = AlertCloseRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Resolve/close an alert following clinical action."""
    alert = get_alert_by_id(db, id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    check_patient_access(current_user, alert.patient_id, db)
    return close_alert(db, id, doctor_user_id=current_user.id, clinical_note=close_in.clinical_note)


@router.post("/alerts/{id}/patient-acknowledge", response_model=AlertOut)
def patient_acknowledge_alert_route(
    id: int,
    ack_in: AlertPatientAcknowledgeRequest = AlertPatientAcknowledgeRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Patient confirms reading emergency guidance (UC09b / RS-1)."""
    alert = get_alert_by_id(db, id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="help")
    if alert.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return patient_acknowledge_alert(db, id, patient_user_id=current_user.id)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
