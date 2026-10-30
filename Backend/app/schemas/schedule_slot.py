"""Pydantic schemas for the ScheduleSlot entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ScheduleSlotBase(BaseModel):
    schedule_id: int
    scheduled_at: Optional[datetime] = None
    status: str = "pending"
    reading_id: Optional[int] = None
    completed_at: Optional[datetime] = None


class ScheduleSlotCreate(ScheduleSlotBase):
    pass


class ScheduleSlotUpdate(BaseModel):
    status: Optional[str] = None
    reading_id: Optional[int] = None
    completed_at: Optional[datetime] = None


class ScheduleSlotOut(BaseModel):
    id: int
    schedule_id: int
    scheduled_at: datetime
    status: str
    reading_id: Optional[int] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
