"""Pydantic schemas for the DoctorProfile entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DoctorProfileBase(BaseModel):
    user_id: int
    license_number: str
    specialization: Optional[str] = None
    phone: Optional[str] = None


class DoctorProfileCreate(DoctorProfileBase):
    pass


class DoctorProfileUpdate(BaseModel):
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None


class DoctorProfileOut(BaseModel):
    id: int
    user_id: int
    license_number: str
    specialization: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
