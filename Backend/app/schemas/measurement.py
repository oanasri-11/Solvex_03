"""Pydantic schemas for the BloodPressureReading entity."""

from datetime import datetime
<<<<<<< HEAD
from typing import Optional

from pydantic import BaseModel, ConfigDict
=======
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class BloodPressureReadingBase(BaseModel):
    patient_id: int
<<<<<<< HEAD
    systolic: int
    diastolic: int
    measured_at: Optional[datetime] = None
    recheck_of_reading_id: Optional[int] = None
=======
    systolic: int = Field(..., ge=40, le=300)
    diastolic: int = Field(..., ge=30, le=200)
    pulse: Optional[int] = Field(None, ge=30, le=250)
    measured_at: Optional[datetime] = None
    session_id: Optional[str] = None
    slot_id: Optional[int] = None
    capture_method: Optional[str] = "manual"  # manual, assisted, low_bandwidth_sms, connected_device
    entered_by: Optional[str] = "patient"  # patient, caregiver, professional, device
    actor_id: Optional[int] = None
    symptoms_reported: Optional[List[str]] = None
    medication_taken_today: Optional[bool] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    notes: Optional[str] = None


class BloodPressureReadingCreate(BloodPressureReadingBase):
    pass


<<<<<<< HEAD
class BloodPressureReadingUpdate(BaseModel):
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    measured_at: Optional[datetime] = None
    recheck_of_reading_id: Optional[int] = None
=======
class ReadingConfirmRequest(BaseModel):
    """Patient confirming an unusual value (needs_confirmation -> confirmed_by_entrant)."""
    confirmed: bool = True
    note: Optional[str] = None


class ReadingAnnotateRequest(BaseModel):
    """Non-clinical entrant note or contextual tag."""
    note: str
    tags: Optional[List[str]] = None


class BloodPressureReadingUpdate(BaseModel):
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    notes: Optional[str] = None


class BloodPressureReadingOut(BaseModel):
    id: int
    patient_id: int
<<<<<<< HEAD
    systolic: int
    diastolic: int
    measured_at: datetime
    recheck_of_reading_id: Optional[int] = None
=======
    session_id: Optional[str] = None
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    measured_at: datetime
    received_at: Optional[datetime] = None
    capture_method: Optional[str] = "manual"
    entered_by: Optional[str] = "patient"
    actor_id: Optional[int] = None
    slot_id: Optional[int] = None
    mode_at_time: Optional[str] = None
    verification_status: Optional[str] = "accepted"
    status_level: Optional[str] = None
    replaces_reading_id: Optional[int] = None
    recheck_of_reading_id: Optional[int] = None
    symptoms_reported: Optional[List[str]] = None
    medication_taken_today: Optional[bool] = None
    data_quality_flags: Optional[List[str]] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
