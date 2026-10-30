"""Pydantic schemas for OfficeReading entity (Section 7c)."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OfficeReadingCreate(BaseModel):
    systolic: int = Field(..., ge=50, le=300)
    diastolic: int = Field(..., ge=30, le=200)
    pulse: Optional[int] = Field(None, ge=30, le=250)
    measured_at: Optional[datetime] = None
    note: Optional[str] = None


class OfficeReadingOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    measured_at: datetime
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
