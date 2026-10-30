"""Pydantic schemas for the PatientCondition entity."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PatientConditionBase(BaseModel):
    patient_id: int
    condition_name: str
    diagnosed_at: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool


class PatientConditionCreate(PatientConditionBase):
    pass


class PatientConditionUpdate(BaseModel):
    condition_name: Optional[str] = None
    diagnosed_at: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PatientConditionOut(BaseModel):
    id: int
    patient_id: int
    condition_name: str
    diagnosed_at: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
