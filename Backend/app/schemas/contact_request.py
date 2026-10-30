"""Pydantic schemas for the ContactRequest entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContactRequestBase(BaseModel):
    patient_id: int
    doctor_id: Optional[int] = None
    message: str
    status: str


class ContactRequestCreate(ContactRequestBase):
    pass


class ContactRequestUpdate(BaseModel):
    doctor_id: Optional[int] = None
    message: Optional[str] = None
    status: Optional[str] = None
    responded_at: Optional[datetime] = None


class ContactRequestOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    message: str
    status: str
    created_at: datetime
    responded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
