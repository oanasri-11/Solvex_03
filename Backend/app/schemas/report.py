"""Pydantic schemas for Reports & Exports (Section 20)."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ReportExportRequest(BaseModel):
    format: str = "pdf"  # pdf or csv


class ReportExportOut(BaseModel):
    job_id: str
    status: str
    download_url: Optional[str] = None


class ReportPreviewOut(BaseModel):
    patient: Dict[str, Any]
    summary: Dict[str, Any]
    recent_readings_count: int
    treatment_events: List[Dict[str, Any]]
    office_readings: List[Dict[str, Any]]
    recent_alerts_count: int
    generated_at: str
