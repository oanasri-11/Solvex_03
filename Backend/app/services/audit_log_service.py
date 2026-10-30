"""AuditLog service (Section 22, UCAUD, SC6)."""

from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.Auditlog import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate, AuditLogOut


def create_audit_log_entry(db: Session, entry_in: AuditLogCreate) -> Optional[AuditLog]:
    """Append an audit log entry. Verifies the actor exists when set."""
    try:
        user_id = getattr(entry_in, "user_id", None)
        if user_id is not None:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user_id = None

        db_entry = AuditLog(
            user_id=user_id,
            action=entry_in.action,
            table_name=entry_in.table_name,
            record_id=entry_in.record_id,
            old_values=getattr(entry_in, "old_values", None),
            new_values=getattr(entry_in, "new_values", None),
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except SQLAlchemyError:
        db.rollback()
        return None


def get_audit_log_by_id(db: Session, log_id: int) -> Optional[AuditLog]:
    """Retrieve an audit log entry by ID."""
    return db.query(AuditLog).filter(AuditLog.id == log_id).first()


def get_all_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    table_name: Optional[str] = None,
) -> List[AuditLog]:
    """List audit log entries with optional filters."""
    query = db.query(AuditLog)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if table_name is not None:
        query = query.filter(AuditLog.table_name == table_name)
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
