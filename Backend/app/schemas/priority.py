"""Pydantic schemas for the PriorityAssessment entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PriorityAssessmentBase(BaseModel):
    patient_id: int
    assessor_id: Optional[int] = None
    level: str
    assessed_at: Optional[datetime] = None
    notes: Optional[str] = None


class PriorityAssessmentCreate(PriorityAssessmentBase):
    pass


class PriorityAssessmentUpdate(BaseModel):
    level: Optional[str] = None
    assessed_at: Optional[datetime] = None
    notes: Optional[str] = None


class PriorityAssessmentOut(BaseModel):
    id: int
    patient_id: int
    assessor_id: Optional[int] = None
    level: str
    assessed_at: datetime
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
