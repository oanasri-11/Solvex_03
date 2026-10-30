"""Pydantic schemas for ReminderPreference (Section 10)."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ReminderPreferenceUpdate(BaseModel):
    enabled: Optional[bool] = True
    channel: Optional[str] = Field("push", description="push or sms")
    lead_minutes: Optional[int] = Field(15, ge=0, le=60)
    morning_time: Optional[str] = "08:00"
    evening_time: Optional[str] = "20:00"
    routine_day: Optional[str] = "sunday"
    routine_time: Optional[str] = "09:00"
    adaptive_missed_reminder: Optional[bool] = True


class ReminderPreferenceOut(BaseModel):
    id: int
    patient_id: int
    enabled: bool
    channel: str
    lead_minutes: int
    morning_time: Optional[str] = None
    evening_time: Optional[str] = None
    routine_day: Optional[str] = None
    routine_time: Optional[str] = None
    adaptive_missed_reminder: bool
    push_tokens: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)


class PushTokenRequest(BaseModel):
    token: str
    device_name: Optional[str] = None


class ReminderSlotOut(BaseModel):
    slot_id: int
    due_at: str
    window_start: str
    window_end: str
    lead_minutes: int
    channel: str
    message: str
