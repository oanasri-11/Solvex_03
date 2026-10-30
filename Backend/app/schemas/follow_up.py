"""Pydantic schemas for the FollowUpAction entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FollowUpActionBase(BaseModel):
    patient_id: int
    type: str
    status: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class FollowUpActionCreate(FollowUpActionBase):
    pass


class FollowUpActionUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class FollowUpActionOut(BaseModel):
    id: int
    patient_id: int
    type: str
    status: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
