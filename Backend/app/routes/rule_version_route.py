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
    approve_rule_version,
    activate_rule_version,
)
from app.schemas.rule_version import (
    RuleVersionCreate,
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

