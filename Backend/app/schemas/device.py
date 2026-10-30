"""Pydantic schemas for ConnectedDevice and Integrations (Section 11b)."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ConnectedDeviceCreate(BaseModel):
    device_model: str
    serial_number: Optional[str] = None
    mac_address: Optional[str] = None
    validation_status: Optional[str] = "stride_bp_validated"


class ConnectedDeviceOut(BaseModel):
    id: int
    patient_id: int
    device_model: str
    serial_number: Optional[str] = None
    mac_address: Optional[str] = None
    validation_status: str
    paired_at: datetime
    last_sync_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InboundSMSWebhook(BaseModel):
    sender_phone: str
    message: str
    source_message_id: Optional[str] = None


class DeviceSyncItem(BaseModel):
    patient_id: int
    device_record_id: Optional[str] = None
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    measured_at: Optional[datetime] = None


class DeviceBatchSyncRequest(BaseModel):
    items: List[DeviceSyncItem]
