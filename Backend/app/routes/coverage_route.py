"""Coverage and Escalation Targets API routes (Section 4b)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
)
from app.models.user import User
from app.services.coverage_service import (
    get_all_coverage_entries,
    get_coverage_for_doctor,
    set_coverage_for_doctor,
)
from app.schemas.coverage import (
    CoverageTargetCreate,
    CoverageTargetUpdate,
    CoverageTargetOut,
)

router = APIRouter(tags=["coverage"])


@router.get("/admin/coverage", response_model=List[CoverageTargetOut])
def admin_get_all_coverage(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """All clinician coverage and escalation entries - Admin only."""
    return get_all_coverage_entries(db)


@router.put("/admin/coverage/{doctor_id}", response_model=CoverageTargetOut)
def admin_set_doctor_coverage(
    doctor_id: int,
    coverage_in: CoverageTargetUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Set backup and after-hours owner for a doctor - Admin only."""
    try:
        return set_coverage_for_doctor(db, doctor_id, coverage_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/doctor/me/coverage")
def doctor_get_own_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Own backup doctor and who is covering me."""
    if not current_user.doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return get_coverage_for_doctor(db, current_user.doctor_profile.id)
