"""Pydantic schemas for CoverageTarget entity (Section 4b)."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class CoverageTargetCreate(BaseModel):
    doctor_id: int
    backup_doctor_id: Optional[int] = None
    after_hours_owner_id: Optional[int] = None
    coverage_hours: Optional[Dict[str, Any]] = None


class CoverageTargetUpdate(BaseModel):
    backup_doctor_id: Optional[int] = None
    after_hours_owner_id: Optional[int] = None
    coverage_hours: Optional[Dict[str, Any]] = None


class CoverageTargetOut(BaseModel):
    id: int
    doctor_id: int
    backup_doctor_id: Optional[int] = None
    after_hours_owner_id: Optional[int] = None
    coverage_hours: Optional[Dict[str, Any]] = None
    version: int = 1
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
