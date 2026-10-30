"""Audit service (alias for audit_log_service)."""

from app.services.audit_log_service import (
    create_audit_log_entry,
    get_audit_log_by_id,
    get_all_audit_logs,
)

# Friendly aliases matching prompt conventions
create_audit_log = create_audit_log_entry
get_audit_log = get_audit_log_by_id
list_audit_logs = get_all_audit_logs

__all__ = [
    "create_audit_log_entry",
    "get_audit_log_by_id",
    "get_all_audit_logs",
    "create_audit_log",
    "get_audit_log",
    "list_audit_logs",
]

