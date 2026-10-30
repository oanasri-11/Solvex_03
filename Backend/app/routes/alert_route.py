"""Alert routes: CRUD for Alert model."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
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