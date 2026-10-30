

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.Auditlog import AuditLog
from app.models.User import User# type: ignore
from app.schemas.audit_log import AuditLogCreate, AuditLogUpdate, AuditLogOut


def create_audit_log_entry(db: Session, entry_in: AuditLogCreate) -> Optional[AuditLog]:
    """Append an audit log entry. Verifies the actor exists when set."""
    try:
        if entry_in.user_id is not None:
            user = db.query(User).filter(User.id == entry_in.user_id).first()
            if not user:
                return None
        db_entry = AuditLog(
            user_id=entry_in.user_id,
            action=entry_in.action,
            table_name=entry_in.table_name,
            record_id=getattr(entry_in, "record_id", None),
            old_values=getattr(entry_in, "old_values", None),
            new_values=getattr(entry_in, "new_values", None),
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except SQLAlchemyError:
        db.rollback()
        raise


def get_audit_log_by_id(db: Session, entry_id: int) -> Optional[AuditLog]:
    """Retrieve an audit log entry by its primary key."""
    return db.query(AuditLog).filter(AuditLog.id == entry_id).first()


def get_all_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    actor_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
):
    """Search audit log entries with optional actor / entity_type / entity_id filters."""
    query = db.query(AuditLog)
    if actor_id is not None:
        query = query.filter(AuditLog.user_id == actor_id)
    if entity_type is not None:
        query = query.filter(AuditLog.table_name == entity_type)
    if entity_id is not None:
        query = query.filter(AuditLog.record_id == entity_id)
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


# Note: update/delete are intentionally omitted. The audit log is append-only per the
# specification.
