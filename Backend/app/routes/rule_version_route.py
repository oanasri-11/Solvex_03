
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.rule_version_service import (
    get_rule_version_by_id,
    get_rule_version_by_version,
    get_all_rule_versions,
)

from app.schemas.rule_version import RuleVersionOut


router = APIRouter(
    prefix="/rule-versions",
    tags=["Rule Versions"],
)


# Helper: Only doctors can access rule versions
def _require_doctor(current_user: User) -> None:
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )

    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )


# 1. List rule versions
@router.get("/", response_model=List[RuleVersionOut])
def list_rule_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_doctor(current_user)

    return get_all_rule_versions(
        db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )


# 2. Get rule version by version string
# Keep this route before /{version_id}.
@router.get("/by-version/{version}", response_model=RuleVersionOut)
def get_rule_version_by_version_str(
    version: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_doctor(current_user)

    found = get_rule_version_by_version(
        db,
        version,
    )

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule version not found",
        )

    return found


# 3. Get rule version by ID
@router.get("/{version_id}", response_model=RuleVersionOut)
def get_rule_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _require_doctor(current_user)

    version = get_rule_version_by_id(
        db,
        version_id,
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule version not found",
        )

    return version


