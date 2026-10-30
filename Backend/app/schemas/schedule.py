"""Pydantic schemas for the MeasurementSchedule entity."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class MeasurementScheduleBase(BaseModel):
    patient_id: int
    frequency: str
    time_of_day: Optional[str] = None
    days_of_week: Optional[Any] = None
    is_active: bool = True


class MeasurementScheduleCreate(MeasurementScheduleBase):
    pass


class MeasurementScheduleUpdate(BaseModel):
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None
    days_of_week: Optional[Any] = None
    is_active: Optional[bool] = None


class MeasurementScheduleOut(BaseModel):
    id: int
    patient_id: int
    frequency: str
    time_of_day: Optional[str] = None
    days_of_week: Optional[Any] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
