"""Pydantic schemas for CaregiverLink entity (Section 5b)."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CaregiverInvitationRequest(BaseModel):
    """Patient invites a caregiver."""
    name: str
    contact: str = Field(..., description="Phone or email")
    scope: List[str] = Field(
        default=["record", "confirm_slot", "view_history", "view_trend", "reminders", "help"],
        description="Allowed actions for caregiver",
    )
    consent_id: Optional[int] = None
    notify_reminders: bool = True


class CaregiverInvitationResponse(BaseModel):
    id: int
    invite_code: str
    patient_id: int
    caregiver_name: Optional[str] = None
    scope: List[str]
    status: str
    message: str = "Caregiver invitation created successfully"


class CaregiverLinkOut(BaseModel):
    id: int
    patient_id: int
    caregiver_user_id: Optional[int] = None
    invite_code: Optional[str] = None
    caregiver_name: Optional[str] = None
    caregiver_contact: Optional[str] = None
    scope: List[str]
    notify_reminders: bool
    status: str
    consent_id: Optional[int] = None
    created_at: datetime
    revoked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
