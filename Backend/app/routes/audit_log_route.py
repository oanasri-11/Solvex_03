<<<<<<< HEAD

from typing import List, Optional

=======
"""AuditLog API routes (Section 22, SC6)."""

from typing import List, Optional
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
<<<<<<< HEAD
from app.core.deps import get_current_active_user
from app.models.user import User

from app.services.audit_log_service import (
    create_audit_log_entry,
    get_audit_log_by_id,
    get_all_audit_logs,
)

from app.schemas.audit_log import (
    AuditLogCreate,
    AuditLogOut,
)


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.post(
    "/",
    response_model=AuditLogOut,
    status_code=status.HTTP_201_CREATED
)
def create_audit_log(
    entry_in: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an audit log entry."""

    # Only authenticated doctors can create audit log entries.
    if current_user.role != "doctor": # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create audit log entries",
        )

    entry = create_audit_log_entry(db, entry_in)

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with this audit entry was not found",
        )

    return entry


@router.get(
    "/",
    response_model=List[AuditLogOut]
)
def get_all_audit_logs_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    actor_id: Optional[int] = Query(None, gt=0),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve audit logs with optional filters."""

    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view audit logs",
        )

    return get_all_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )


@router.get(
    "/{entry_id}",
    response_model=AuditLogOut
)
def get_audit_log_route(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve an audit log entry by ID."""

    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view audit logs",
        )

    entry = get_audit_log_by_id(db, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log entry not found",
        )

    return entry
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
