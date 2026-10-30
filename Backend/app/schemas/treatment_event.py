"""Pydantic schemas for TreatmentEvent entity (Section 7b)."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class TreatmentEventCreate(BaseModel):
    event_type: str = Field(..., description="started, dose_changed, stopped")
    drug_class: str = Field(..., description="ACEi, ARB, CCB, Thiazide, BB, etc.")
    drug_name: str
    dose: str
    effective_date: date
    note: Optional[str] = None


class TreatmentEventCorrect(BaseModel):
    event_type: str
    drug_class: str
    drug_name: str
    dose: str
    effective_date: date
    note: Optional[str] = None


class TreatmentEventOut(BaseModel):
    id: int
    patient_id: int
    event_type: str
    drug_class: str
    drug_name: str
    dose: str
    effective_date: date
    recorded_by: int
    corrects_event_id: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurrentMedicationsOut(BaseModel):
    patient_id: int
    current_medications: List[TreatmentEventOut]
    antihypertensive_class_count: int
