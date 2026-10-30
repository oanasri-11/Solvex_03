"""Pydantic schemas for the BloodPressureReading entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BloodPressureReadingBase(BaseModel):
    patient_id: int
    systolic: int
    diastolic: int
    measured_at: Optional[datetime] = None
    recheck_of_reading_id: Optional[int] = None
    notes: Optional[str] = None


class BloodPressureReadingCreate(BloodPressureReadingBase):
    pass


class BloodPressureReadingUpdate(BaseModel):
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    measured_at: Optional[datetime] = None
    recheck_of_reading_id: Optional[int] = None
    notes: Optional[str] = None


class BloodPressureReadingOut(BaseModel):
    id: int
    patient_id: int
    systolic: int
    diastolic: int
    measured_at: datetime
    recheck_of_reading_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
