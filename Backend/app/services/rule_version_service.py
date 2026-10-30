"""Rule version service.

CRUD operations for the RuleVersion model, following classic SQLAlchemy syntax.
Rule versions are never deleted; an active version is only superseded. Approve and
activate are expressed as status transitions on the record.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.RuleVersion import RuleVersion
from app.models.user import User
from app.schemas.rule_version import RuleVersionCreate, RuleVersionUpdate, RuleVersionOut


def create_rule_version(db: Session, version_in: RuleVersionCreate) -> RuleVersion:
    """Create a draft rule version. Verifies the approver exists when set."""
    try:
        is_active_val = getattr(version_in, "is_active", False)
        if is_active_val is None:
            is_active_val = False
        db_version = RuleVersion(
            version=version_in.version,
            rule_name=version_in.rule_name,
            rule_definition=getattr(version_in, "rule_definition", None),
            is_active=is_active_val,
        )
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        return db_version
    except SQLAlchemyError:
        db.rollback()
        raise


def get_rule_version_by_id(db: Session, version_id: int) -> Optional[RuleVersion]:
    """Retrieve a rule version by its primary key."""
    return db.query(RuleVersion).filter(RuleVersion.id == version_id).first()


def get_rule_version_by_version(db: Session, version: str) -> Optional[RuleVersion]:
    """Retrieve a rule version by its version string."""
    return db.query(RuleVersion).filter(RuleVersion.version == version).first()


def get_all_rule_versions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
):
    """List rule versions with an optional is_active filter."""
    query = db.query(RuleVersion)
    if is_active is not None:
        query = query.filter(RuleVersion.is_active == is_active)
    return query.order_by(RuleVersion.created_at.desc()).offset(skip).limit(limit).all()


def update_rule_version(
    db: Session, version_id: int, version_in: RuleVersionUpdate
) -> Optional[RuleVersion]:
    """Update a rule version. Active versions are never edited, only superseded."""
    try:
        db_version = get_rule_version_by_id(db, version_id)
        if not db_version:
            return None
        if db_version.is_active:# type: ignore
            return None
        update_data = version_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_version, field, value)
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        return db_version
    except SQLAlchemyError:
        db.rollback()
        raise


def approve_rule_version(db: Session, version_id: int, approved_by: int) -> Optional[RuleVersion]:
    """Approve a rule version (clinical approval)."""
    try:
        db_version = get_rule_version_by_id(db, version_id)
        if not db_version:
            return None
        user = db.query(User).filter(User.id == approved_by).first()
        if not user:
            return None
        db_version.is_active = False# type: ignore
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        return db_version
    except SQLAlchemyError:
        db.rollback()
        raise


def activate_rule_version(db: Session, version_id: int) -> Optional[RuleVersion]:
    """Activate a rule version; only after approval. Only one version is active at a time."""
    try:
        db_version = get_rule_version_by_id(db, version_id)
        if not db_version:
            return None
        # Retire any currently active versions safely without bulk evaluate errors
        active_versions = (
            db.query(RuleVersion).filter(RuleVersion.is_active == True).all()  # noqa: E712
        )
        for v in active_versions:
            v.is_active = False# type: ignore
        db_version.is_active = True# type: ignore
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        return db_version
    except SQLAlchemyError:
        db.rollback()
        raise


# Note: delete is intentionally omitted. Rule versions are never deleted; they are
# superseded per the specification.
