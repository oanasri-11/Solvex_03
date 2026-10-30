
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

from app.services.alert_service import (
    get_alert_by_id,
    get_all_alerts,
    update_alert,
    acknowledge_alert,
    close_alert,
)

from app.services.patient_service import (
    get_patient_profile_by_user_id,
)

from app.services.assignment_service import (
    is_doctor_assigned,
    get_all_assignments,
)

from app.schemas.alert import AlertUpdate, AlertOut


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


# Check whether the current user can access an alert
def _require_alert_access(
    current_user: User,
    alert,
    db: Session,
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile or profile.id != alert.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access this alert",
            )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        if not is_doctor_assigned(
            db,
            current_user.doctor_profile.id,
            alert.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or patient not assigned to doctor",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# 1. List accessible alerts
@router.get("/", response_model=List[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    alert_status: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile:
            return []

        if patient_id is not None and patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another patient's alerts",
            )

        return get_all_alerts(
            db,
            skip=skip,
            limit=limit,
            patient_id=profile.id,# type: ignore
            lifecycle=alert_status,
            severity_level=severity,
        )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        assignments = get_all_assignments(
            db,
            doctor_id=current_user.doctor_profile.id,
            active=True,
        )

        allowed_patient_ids = {
            assignment.patient_id for assignment in assignments
        }

        if patient_id is not None:
            if patient_id not in allowed_patient_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Patient is not assigned to you",
                )

            allowed_patient_ids = {patient_id}

        all_alerts = get_all_alerts(
            db,
            skip=0,
            limit=10000,
            lifecycle=alert_status,
            severity_level=severity,
        )

        accessible_alerts = [
            alert for alert in all_alerts
            if alert.patient_id in allowed_patient_ids
        ]

        return accessible_alerts[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to list alerts",
    )


# 2. Get alert by ID
@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_alert = get_alert_by_id(db, alert_id)

    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    _require_alert_access(current_user, db_alert, db)

    return db_alert


# 3. Update alert
# Only doctors can update alerts
@router.put("/{alert_id}", response_model=AlertOut)
def update_alert_route(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update alerts",
        )

    db_alert = get_alert_by_id(db, alert_id)

    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    _require_alert_access(current_user, db_alert, db)

    updated = update_alert(db, alert_id, alert_in)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return updated


# 4. Acknowledge alert
@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert_route(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can acknowledge alerts",
        )

    db_alert = get_alert_by_id(db, alert_id)

    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    _require_alert_access(current_user, db_alert, db)

    updated = acknowledge_alert(
        db,
        alert_id,
        current_user.id,# type: ignore
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alert cannot be acknowledged",
        )

    return updated


# 5. Close alert
@router.post("/{alert_id}/close", response_model=AlertOut)
def close_alert_route(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can close alerts",
        )

    db_alert = get_alert_by_id(db, alert_id)

    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    _require_alert_access(current_user, db_alert, db)

    updated = close_alert(
        db,
        alert_id,
        current_user.id,# type: ignore
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alert cannot be closed",
        )

    return updated
