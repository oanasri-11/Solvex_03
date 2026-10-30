"""Pydantic schemas for the ScheduleSlot entity."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ScheduleSlotBase(BaseModel):
    schedule_id: int
    cycle_id: Optional[str] = None
    patient_id: int
    due_at: datetime
    window_start: datetime
    window_end: datetime
    readings_required: int = 2
    readings_received: int = 0
    status: str = "upcoming"  # upcoming, taken, partial, not_taken, missed
    reading_ids: Optional[List[int]] = None
    reason: Optional[str] = None


class ScheduleSlotCreate(ScheduleSlotBase):
    pass


class SlotConfirmRequest(BaseModel):
    """Close a slot (F15)."""
    taken: bool
    reading_ids: Optional[List[int]] = None
    reason: Optional[str] = None


class ScheduleSlotUpdate(BaseModel):
    status: Optional[str] = None
    readings_received: Optional[int] = None
    reading_ids: Optional[List[int]] = None
    reason: Optional[str] = None
    closed_at: Optional[datetime] = None


class ScheduleSlotOut(BaseModel):
    id: int
    schedule_id: int
    cycle_id: Optional[str] = None
    patient_id: int
    due_at: datetime
    window_start: datetime
    window_end: datetime
    readings_required: int
    readings_received: int
    status: str
    reading_ids: Optional[List[int]] = None
    reason: Optional[str] = None
    closed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
