"""Pydantic schemas for the MeasurementSchedule entity."""

from datetime import datetime, date
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, ConfigDict


class MeasurementScheduleBase(BaseModel):
    patient_id: int
    owner: str = "patient"  # patient, doctor
    protocol: str = "722_followup"  # 722_diagnostic, 722_followup, maintenance, custom
    readings_per_slot: int = 2
    min_gap_seconds: int = 60
    windows: Optional[Dict[str, Any]] = None  # morning and evening windows
    cycle_length_days: Optional[int] = 7
    pattern: Optional[str] = "daily"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: Optional[str] = "twice_daily"
    is_active: bool = True


class MeasurementScheduleCreate(MeasurementScheduleBase):
    pass


class MeasurementScheduleUpdate(BaseModel):
    owner: Optional[str] = None
    protocol: Optional[str] = None
    readings_per_slot: Optional[int] = None
    min_gap_seconds: Optional[int] = None
    windows: Optional[Dict[str, Any]] = None
    cycle_length_days: Optional[int] = None
    pattern: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None


class MeasurementScheduleOut(BaseModel):
    id: int
    patient_id: int
    owner: str
    protocol: str
    readings_per_slot: int
    min_gap_seconds: int
    windows: Optional[Dict[str, Any]] = None
    cycle_length_days: Optional[int] = None
    pattern: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    version: int = 1
    is_active: bool
    pending_approval: bool = False
    created_by: Optional[int] = None
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
