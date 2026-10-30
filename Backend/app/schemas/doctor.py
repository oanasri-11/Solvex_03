"""Pydantic schemas for the DoctorProfile entity."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class DoctorProfileBase(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    license_number: str
    specialization: Optional[str] = None
    speciality: Optional[str] = None
    facility: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    notification_preferences: Optional[Dict[str, Any]] = None


class DoctorProfileCreate(DoctorProfileBase):
    pass


class DoctorProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    speciality: Optional[str] = None
    facility: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Any]] = None


class DoctorNotificationPreferencesUpdate(BaseModel):
    """Notification channels per alert response tier (in_app, email, sms)."""
    routine_out_of_range: Optional[List[str]] = ["in_app"]
    persistent_elevation: Optional[List[str]] = ["in_app", "email"]
    severe_single_reading: Optional[List[str]] = ["in_app", "email", "sms"]
    critical_emergency: List[str] = ["in_app", "email", "sms"]  # must have at least 2 channels


class DoctorProfileOut(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    license_number: str
    specialization: Optional[str] = None
    speciality: Optional[str] = None
    facility: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    notification_preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
