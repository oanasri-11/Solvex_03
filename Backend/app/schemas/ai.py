"""Pydantic schemas for AI Clinical Summarization (Section 23)."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class AISummaryResponse(BaseModel):
    is_draft: bool = True
    requires_clinician_approval: bool = True
    patient_id: int
    draft_summary: str
    clinical_digest_data: Dict[str, Any]
    generated_at: str


class AIAlertExplanationResponse(BaseModel):
    is_draft: bool = True
    requires_clinician_approval: bool = True
    alert_id: int
    patient_id: int
    draft_explanation: str
    generated_at: str
