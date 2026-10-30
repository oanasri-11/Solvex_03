"""Pydantic schemas for the ScheduleSlot entity."""

from datetime import datetime
<<<<<<< HEAD
from typing import Optional

=======
from typing import Optional, List
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from pydantic import BaseModel, ConfigDict


class ScheduleSlotBase(BaseModel):
    schedule_id: int
<<<<<<< HEAD
    scheduled_at: Optional[datetime] = None
    status: str = "pending"
    reading_id: Optional[int] = None
    completed_at: Optional[datetime] = None
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class ScheduleSlotCreate(ScheduleSlotBase):
    pass


<<<<<<< HEAD
class ScheduleSlotUpdate(BaseModel):
    status: Optional[str] = None
    reading_id: Optional[int] = None
    completed_at: Optional[datetime] = None
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class ScheduleSlotOut(BaseModel):
    id: int
    schedule_id: int
<<<<<<< HEAD
    scheduled_at: datetime
    status: str
    reading_id: Optional[int] = None
    completed_at: Optional[datetime] = None
=======
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
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489

    model_config = ConfigDict(from_attributes=True)
