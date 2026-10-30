"""Pydantic schemas for Consent entity (Section 6, SC5)."""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict, Field


class ConsentCreate(BaseModel):
    type: str = Field(..., description="data_sharing, monitoring_mode, caregiver_access")
    text_version: str = Field("v1.0", description="Version of consent text accepted")
    accepted: bool = Field(True, description="Must be true to record consent")
    method: Optional[str] = "in_app"  # in_app, paper, verbal
    witness_note: Optional[str] = None


class ConsentAdminCreate(ConsentCreate):
    """Admin creating consent on patient behalf at enrolment."""
    method: str = Field(..., description="paper or verbal")
    witness_note: Optional[str] = None


class ConsentOut(BaseModel):
    id: int
    patient_id: int
    type: str
    text_version: str
    accepted_at: datetime
    withdrawn_at: Optional[datetime] = None
    recorded_by: int
    method: str
    witness_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConsentTextOut(BaseModel):
    version: str
    language: str
    title: str
    text: str


class ConsentStateOut(BaseModel):
    patient_id: int
    data_sharing: bool
    monitoring_mode: bool
    caregiver_access: bool
    consents: Dict[str, Optional[int]] = {}
