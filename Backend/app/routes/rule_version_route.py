<<<<<<< HEAD
"""Rule version routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Rule versions are never deleted; an active version is only superseded. Admin only.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_active_user, get_current_admin
from app.models.user import User
from app.services.rule_version_service import (
    create_rule_version,
    get_rule_version_by_id,
    get_rule_version_by_version,
    get_all_rule_versions,
    update_rule_version,
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    approve_rule_version,
    activate_rule_version,
)
from app.schemas.rule_version import (
    RuleVersionCreate,
<<<<<<< HEAD
    RuleVersionUpdate,
    RuleVersionOut,
)

router = APIRouter(prefix="/rule-versions", tags=["rule-versions"])


def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )


@router.get("/", response_model=List[RuleVersionOut])
def list_rule_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
):
    """List rule versions (admin only)."""
    _require_admin(current_user)
    return get_all_rule_versions(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/{version_id}", response_model=RuleVersionOut)
def get_rule_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a rule version by ID (admin only)."""
    _require_admin(current_user)
    version = get_rule_version_by_id(db, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found"
        )
    return version


@router.get("/by-version/{version}", response_model=RuleVersionOut)
def get_rule_version_by_version_str(
    version: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a rule version by its version string (admin only)."""
    _require_admin(current_user)
    found = get_rule_version_by_version(db, version)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found"
        )
    return found


@router.post(
    "/",
    response_model=RuleVersionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_rule_version_route(
    version_in: RuleVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a draft rule version (admin only)."""
    _require_admin(current_user)
    return create_rule_version(db, version_in)


@router.put("/{version_id}", response_model=RuleVersionOut)
def update_rule_version_route(
    version_id: int,
    version_in: RuleVersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a rule version. Active versions are never edited (admin only)."""
    _require_admin(current_user)
    updated = update_rule_version(db, version_id, version_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule version not found or is active",
        )
    return updated


@router.post("/{version_id}/approve", response_model=RuleVersionOut)
def approve_rule_version_route(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Approve a rule version (admin only)."""
    _require_admin(current_user)
    approved = approve_rule_version(db, version_id, current_user.id)# type: ignore
    if not approved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found"
        )
    return approved


@router.post("/{version_id}/activate", response_model=RuleVersionOut)
def activate_rule_version_route(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Activate a rule version (admin only)."""
    _require_admin(current_user)
    activated = activate_rule_version(db, version_id)
    if not activated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found"
        )
    return activated

=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
