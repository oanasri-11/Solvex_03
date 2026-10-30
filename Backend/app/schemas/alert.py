"""Pydantic schemas for the Alert entity."""

from datetime import datetime
<<<<<<< HEAD
from typing import Optional

=======
from typing import Optional, List, Dict, Any
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    patient_id: int
    alert_type: str
    severity: str
<<<<<<< HEAD
    status: str = "new"
=======
    tier: Optional[str] = "routine_out_of_range"  # routine_out_of_range, persistent_elevation, severe_single_reading, critical_emergency
    trigger_type: Optional[str] = "single_reading"  # single_reading, trend_persistence, missed_data
    status: str = "new"
    lifecycle: Optional[str] = "raised"  # raised, delivered, acknowledged, escalated, closed
    rule_version_id: Optional[int] = None
    justification: Optional[Dict[str, Any]] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    message: Optional[str] = None


class AlertCreate(AlertBase):
<<<<<<< HEAD
    pass
=======
    reading_ids: Optional[List[int]] = None


class AlertAcknowledgeRequest(BaseModel):
    note: Optional[str] = None


class AlertPatientAcknowledgeRequest(BaseModel):
    """Patient confirms reading emergency guidance (UC09b / RS-1)."""
    confirmed: bool = True
    action_taken: Optional[str] = None


class AlertCloseRequest(BaseModel):
    clinical_note: Optional[str] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class AlertUpdate(BaseModel):
    severity: Optional[str] = None
<<<<<<< HEAD
    status: Optional[str] = None
=======
    tier: Optional[str] = None
    status: Optional[str] = None
    lifecycle: Optional[str] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    message: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertOut(BaseModel):
    id: int
    patient_id: int
    alert_type: str
    severity: str
<<<<<<< HEAD
    status: str
    message: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
=======
    tier: Optional[str] = "routine_out_of_range"
    trigger_type: Optional[str] = "single_reading"
    status: str
    lifecycle: Optional[str] = "raised"
    rule_version_id: Optional[int] = None
    justification: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    created_at: datetime
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    escalated_to_user_id: Optional[int] = None
    closed_by: Optional[int] = None
    closed_at: Optional[datetime] = None
    patient_acknowledged_at: Optional[datetime] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
