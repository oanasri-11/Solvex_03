"""Pydantic schemas for System Config (Section 15)."""

from typing import Dict, Any, List
from pydantic import BaseModel


class RedFlagSymptom(BaseModel):
    code: str
    label: str


class PatientContentResponse(BaseModel):
    emergency_numbers: Dict[str, str]
    emergency_guidance: str
    urgent_repeat_guidance: str
    red_flag_symptoms: List[RedFlagSymptom]
    language: str


class LabelsResponse(BaseModel):
    status_levels: Dict[str, str]
    alert_tiers: Dict[str, str]
    priority_levels: Dict[str, str]
    data_quality_warnings: Dict[str, str]
    language: str


class FeaturesResponse(BaseModel):
    features: Dict[str, bool]
