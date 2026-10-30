"""Pydantic schemas for the PatientHelpRequest entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PatientHelpRequestBase(BaseModel):
    patient_id: int
    type: str
    status: str
    description: Optional[str] = None


class PatientHelpRequestCreate(PatientHelpRequestBase):
    pass


class PatientHelpRequestUpdate(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    resolved_at: Optional[datetime] = None


class PatientHelpRequestOut(BaseModel):
    id: int
    patient_id: int
    type: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
