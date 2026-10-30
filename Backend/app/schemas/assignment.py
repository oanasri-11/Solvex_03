"""Pydantic schemas for the DoctorPatientAssignment entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DoctorPatientAssignmentBase(BaseModel):
    doctor_id: int
    patient_id: int
    assigned_at: Optional[datetime] = None
    is_active: bool = True


class DoctorPatientAssignmentCreate(DoctorPatientAssignmentBase):
    pass


class DoctorPatientAssignmentUpdate(BaseModel):
    doctor_id: Optional[int] = None
    patient_id: Optional[int] = None
    is_active: Optional[bool] = None


class DoctorPatientAssignmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    assigned_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
