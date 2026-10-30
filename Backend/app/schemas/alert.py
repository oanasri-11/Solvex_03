"""Pydantic schemas for the Alert entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    patient_id: int
    alert_type: str
    severity: str
    status: str = "new"
    message: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    severity: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertOut(BaseModel):
    id: int
    patient_id: int
    alert_type: str
    severity: str
    status: str
    message: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
