"""Pydantic schemas for the CaseReview entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CaseReviewBase(BaseModel):
    patient_id: int
    reviewer_id: Optional[int] = None
    status: str
    reviewed_at: Optional[datetime] = None
    summary: Optional[str] = None


class CaseReviewCreate(CaseReviewBase):
    pass


class CaseReviewUpdate(BaseModel):
    reviewer_id: Optional[int] = None
    status: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    summary: Optional[str] = None


class CaseReviewOut(BaseModel):
    id: int
    patient_id: int
    reviewer_id: Optional[int] = None
    status: str
    reviewed_at: Optional[datetime] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
