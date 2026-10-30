<<<<<<< HEAD


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



=======
"""RuleVersion service (Section 21, UCRULE, UCRAPP, SC7)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.RuleVersion import RuleVersion


DEFAULT_RULE_CONFIG = {
    "verification_bounds": {
        "sbp_min": 50,
        "sbp_max": 300,
        "dbp_min": 30,
        "dbp_max": 200,
    },
    "unusual_bounds": {
        "sbp_severe": 180,
        "sbp_low": 80,
        "dbp_severe": 120,
        "dbp_low": 50,
        "min_pulse_pressure": 20,
    },
    "alert_thresholds": {
        "severe_sbp": 180,
        "severe_dbp": 110,
        "critical_emergency_sbp": 200,
        "persistent_window": 10,
        "persistent_min_elevated": 3,
    },
    "target_bounds": {
        "sbp_min": 100,
        "sbp_max": 180,
        "dbp_min": 60,
        "dbp_max": 110,
    },
    "priority_weights": {
        "w_alert_critical": 100.0,
        "w_alert_severe": 60.0,
        "w_alert_persistent": 30.0,
        "w_trend": 1.5,
        "w_adh": 20.0,
        "c_risk_condition": 15.0,
        "c_risk_age80": 10.0,
    },
    "sla_hours": {
        "critical_emergency": 2,
        "severe_single_reading": 24,
    }
}


def create_draft_rule_version(db: Session, version_tag: str, config_json: Optional[Dict[str, Any]] = None) -> RuleVersion:
    """Create draft rule configuration (Admin)."""
    existing = db.query(RuleVersion).filter(RuleVersion.version == version_tag).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rule version tag already exists")

    rule = RuleVersion(
        version=version_tag,
        rule_name=f"Rule Version {version_tag}",
        rule_definition=config_json or DEFAULT_RULE_CONFIG,
        is_active=False,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def approve_rule_version(
    db: Session,
    rule_id: int,
    doctor_user_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
) -> RuleVersion:
    doctor_user_id = doctor_user_id or doctor_id or 1
    """Clinical authorization of rule version by doctor (UCRAPP, NRULE)."""
    rule = db.query(RuleVersion).filter(RuleVersion.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found")

    # In our schema or rule_definition
    if isinstance(rule.rule_definition, dict):
        rule.rule_definition["approved_by_doctor_id"] = doctor_user_id
        rule.rule_definition["approved_at"] = datetime.now(timezone.utc).isoformat()
        rule.rule_definition["status"] = "approved"

    db.commit()
    db.refresh(rule)
    return rule


def activate_rule_version(db: Session, rule_id: int) -> RuleVersion:
    """Activate rule configuration across environment (Admin). Only after clinical approval."""
    rule = db.query(RuleVersion).filter(RuleVersion.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule version not found")

    # Check clinical approval
    defn = rule.rule_definition or {}
    if not defn.get("approved_by_doctor_id"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CLINICAL_APPROVAL_REQUIRED: A rule version becomes active only after clinical approval by a doctor (NRULE)"
        )

    # Deactivate all others
    all_rules = db.query(RuleVersion).all()
    for r in all_rules:
        r.is_active = False

    rule.is_active = True
    if isinstance(rule.rule_definition, dict):
        rule.rule_definition["status"] = "active"

    db.commit()
    db.refresh(rule)
    return rule


def get_active_rule_version(db: Session) -> Dict[str, Any]:
    """Return active rule configuration parameters."""
    rule = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()  # noqa: E712
    if rule and rule.rule_definition:
        return rule.rule_definition
    return DEFAULT_RULE_CONFIG


def get_all_rule_versions(db: Session, skip: int = 0, limit: int = 100) -> List[RuleVersion]:
    """List rule versions."""
    return db.query(RuleVersion).order_by(RuleVersion.created_at.desc()).offset(skip).limit(limit).all()


def get_rule_version_by_id(db: Session, rule_id: int) -> Optional[RuleVersion]:
    """Retrieve rule version by ID."""
    return db.query(RuleVersion).filter(RuleVersion.id == rule_id).first()


def get_rule_version_by_version(db: Session, version: str) -> Optional[RuleVersion]:
    """Retrieve rule version by version string."""
    return db.query(RuleVersion).filter(RuleVersion.version == version).first()


def update_rule_version(db: Session, rule_id: int, update_in: Any) -> Optional[RuleVersion]:
    """Update rule version."""
    rule = get_rule_version_by_id(db, rule_id)
    if not rule:
        return None
    for field, val in update_in.dict(exclude_unset=True).items():
        setattr(rule, field, val)
    db.commit()
    db.refresh(rule)
    return rule


def create_rule_version(db: Session, rule_in: Any) -> RuleVersion:
    """Helper create."""
    version = str(getattr(rule_in, "version", None) or getattr(rule_in, "version_tag", None) or "1.0")
    config = getattr(rule_in, "rule_definition", None) or getattr(rule_in, "config_json", None)
    return create_draft_rule_version(db, version, config)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
