<<<<<<< HEAD
"""Priority assessment routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Priority assessments are backend-computed and immutable; they are never exposed to
patients and never edited or deleted by clients. Access: doctors and admins only.
"""

from typing import List, Optional
=======
"""PriorityAssessment & Doctor Queue API routes (Section 13)."""

from typing import List, Optional, Dict, Any
from datetime import datetime
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
<<<<<<< HEAD
from app.core.deps import get_current_active_user, get_current_admin, get_current_doctor
from app.models.user import User
from app.services.priority_service import (
    create_priority_assessment,
    get_priority_assessment_by_id,
    get_all_priority_assessments,
)
from app.schemas.priority import (
    PriorityAssessmentCreate,
    PriorityAssessmentUpdate,
    PriorityAssessmentOut,
)

router = APIRouter(prefix="/priorities", tags=["priorities"])


def _require_doctor_or_admin(current_user: User) -> None:
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )


@router.get("/", response_model=List[PriorityAssessmentOut])
def list_priority_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
):
    """List priority assessments (doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    return get_all_priority_assessments(
        db, skip=skip, limit=limit, patient_id=patient_id, level=level
    )


@router.get("/{assessment_id}", response_model=PriorityAssessmentOut)
def get_priority_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a priority assessment by ID (doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    assessment = get_priority_assessment_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Priority assessment not found"
        )
    return assessment


@router.post(
    "/",
    response_model=PriorityAssessmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_priority_assessment_route(
    assessment_in: PriorityAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Backend-only creation of a priority assessment (doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    assessment = create_priority_assessment(db, assessment_in)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient or assessor not found",
        )
    return assessment

=======
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.priority_service import (
    get_priority_queue,
    get_priority_queue_updates,
    get_patient_priority_breakdown,
    get_priority_history,
)
from app.services.alert_service import get_alerts_for_doctor
from app.services.assignment_service import get_doctor_patients
from app.services.contact_request_service import get_contact_requests_for_doctor

router = APIRouter(tags=["priority"])


@router.get("/doctor/me/dashboard")
def get_doctor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Workspace counters: active patients, unacknowledged alerts by tier, open contact requests."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")

    doctor_id = current_user.doctor_profile.id

    patients = get_doctor_patients(db, doctor_id)
    alerts = get_alerts_for_doctor(db, doctor_id, unacknowledged_only=True)
    contact_reqs = get_contact_requests_for_doctor(db, doctor_id)

    # Breakdown of unacknowledged alerts by tier
    alert_breakdown = {
        "critical_emergency": 0,
        "severe_single_reading": 0,
        "persistent_elevation": 0,
        "routine_out_of_range": 0,
    }
    for a in alerts:
        tier = a.tier or "routine_out_of_range"
        if tier in alert_breakdown:
            alert_breakdown[tier] += 1

    return {
        "doctor_id": doctor_id,
        "active_patient_count": len(patients),
        "unacknowledged_alerts_count": len(alerts),
        "alerts_by_tier": alert_breakdown,
        "open_contact_requests_count": len(contact_reqs),
    }


@router.get("/doctor/me/priority-queue")
def get_priority_queue_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    search: Optional[str] = Query(None),
    priority_level: Optional[List[str]] = Query(None),
    alert_tier: Optional[List[str]] = Query(None),
    monitoring_mode: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Triage queue (D1) sorted by server-calculated priority score."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")

    return get_priority_queue(
        db,
        doctor_id=current_user.doctor_profile.id,
        search=search,
        priority_levels=priority_level,
        alert_tiers=alert_tier,
        monitoring_mode=monitoring_mode,
        page=page,
        page_size=page_size,
    )


@router.get("/doctor/me/priority-queue/updates")
def get_priority_queue_updates_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    since: Optional[datetime] = Query(None),
):
    """Delta cursor endpoint for queue update badges."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")

    return get_priority_queue_updates(
        db,
        doctor_id=current_user.doctor_profile.id,
        since=since,
    )


@router.get("/doctor/patients/{id}/priority")
def get_patient_priority_breakdown_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Current priority tier with breakdown of clinical and behavioral drivers."""
    check_patient_access(current_user, id, db)
    return get_patient_priority_breakdown(db, id)


@router.get("/doctor/patients/{id}/priority/history")
def get_patient_priority_history_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Priority trajectory audit log."""
    check_patient_access(current_user, id, db)
    return get_priority_history(db, id)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
