"""Pydantic schemas for ModeChangeRequest entity (Section 5)."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ModeChangeRequestCreate(BaseModel):
    requested_mode: str = Field(..., description="self_monitoring or telemonitoring")
    reason: Optional[str] = None


class ModeChangeResolveRequest(BaseModel):
    decision: str = Field(..., description="approved or declined")
    note: Optional[str] = None


class ModeChangeRequestOut(BaseModel):
    id: int
    patient_id: int
    requested_mode: str
    reason: Optional[str] = None
    status: str
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
