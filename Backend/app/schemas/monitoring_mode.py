"""Pydantic schemas for the PatientMonitoringMode entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PatientMonitoringModeBase(BaseModel):
    patient_id: int
    mode: str


class PatientMonitoringModeCreate(PatientMonitoringModeBase):
    pass


class PatientMonitoringModeUpdate(BaseModel):
    mode: Optional[str] = None


class PatientMonitoringModeOut(BaseModel):
    id: int
    patient_id: int
    mode: str
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
