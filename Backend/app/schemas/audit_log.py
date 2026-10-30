"""Pydantic schemas for the AuditLog entity."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    user_id: Optional[int] = None
    action: str
    table_name: str
    record_id: Optional[int] = None
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    action: Optional[str] = None
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    table_name: str
    record_id: Optional[int] = None
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
