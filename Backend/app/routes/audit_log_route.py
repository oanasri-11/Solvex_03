"""AuditLog API routes (Section 22, SC6)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.services.audit_log_service import (
    get_all_audit_logs,
    get_audit_log_by_id,
)
from app.schemas.audit_log import AuditLogOut

router = APIRouter(prefix="/admin/audit-logs", tags=["audit_logs"])


@router.get("", response_model=List[AuditLogOut])
def query_audit_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    user_id: Optional[int] = Query(None),
    table_name: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Query append-only access and write audit logs - Admin only."""
    return get_all_audit_logs(
        db,
        user_id=user_id,
        table_name=table_name,
        action=action,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=AuditLogOut)
def get_single_audit_record(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Single audit record verification - Admin only."""
    log = get_audit_log_by_id(db, id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log record not found")
    return log
