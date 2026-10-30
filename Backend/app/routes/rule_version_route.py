"""RuleVersion API routes (Section 21, SC7)."""

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
from app.services.rule_version_service import (
    get_all_rule_versions,
    get_rule_version_by_id,
    create_draft_rule_version,
    approve_rule_version,
    activate_rule_version,
)
from app.schemas.rule_version import (
    RuleVersionCreate,
    RuleVersionOut,
)

router = APIRouter(prefix="/admin/rule-versions", tags=["rule_versions"])


@router.get("", response_model=List[RuleVersionOut])
def list_rule_versions(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """List system rule versions - Admin only."""
    return get_all_rule_versions(db)


@router.get("/{id}", response_model=RuleVersionOut)
def inspect_rule_version(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Inspect specific threshold and weighting configurations (Admin, Doctor)."""
    if current_user.role not in ("admin", "doctor"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    rv = get_rule_version_by_id(db, id)
    if not rv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found")
    return rv


@router.post("", response_model=RuleVersionOut, status_code=status.HTTP_201_CREATED)
def create_draft_version(
    rv_in: RuleVersionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create draft rule configuration - Admin only."""
    try:
        return create_draft_rule_version(db, rv_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/approve", response_model=RuleVersionOut)
def doctor_approve_version(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Clinical authorization of rule version (Doctor only)."""
    doctor_id = current_user.doctor_profile.id if current_user.doctor_profile else current_user.id
    try:
        return approve_rule_version(db, id, doctor_id=doctor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/activate", response_model=RuleVersionOut)
def admin_activate_version(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Activate rule configuration across environment (Admin only)."""
    try:
        return activate_rule_version(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
