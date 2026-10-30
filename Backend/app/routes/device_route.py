"""Connected Devices & Integrations API routes (Section 11b)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_patient,
)
from app.models.user import User
from app.services.device_service import (
    get_patient_devices,
    pair_device,
    unpair_device,
    process_inbound_sms,
    sync_connected_devices,
)
from app.schemas.device import (
    ConnectedDeviceCreate,
    ConnectedDeviceOut,
    InboundSMSWebhook,
    DeviceBatchSyncRequest,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["devices"])


@router.get("/patients/me/devices", response_model=List[ConnectedDeviceOut])
def get_own_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """List paired blood pressure monitors."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_patient_devices(db, current_user.patient_profile.id)


@router.post("/patients/me/devices", response_model=ConnectedDeviceOut, status_code=status.HTTP_201_CREATED)
def pair_own_device(
    device_in: ConnectedDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Pair a Bluetooth/BLE home monitor."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return pair_device(db, current_user.patient_profile.id, device_in)


@router.delete("/patients/me/devices/{id}", response_model=MessageResponse)
def unpair_own_device(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Unpair a device."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    success = unpair_device(db, current_user.patient_profile.id, id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return MessageResponse(message=f"Device {id} unpaired successfully")


@router.post("/integrations/sms/inbound")
def inbound_sms_webhook(
    sms_in: InboundSMSWebhook,
    db: Session = Depends(get_db),
):
    """Signed webhook for inbound SMS readings (parses structured text replies)."""
    try:
        return process_inbound_sms(
            db,
            sender_phone=sms_in.sender_phone,
            message_text=sms_in.message,
            source_message_id=sms_in.source_message_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post("/integrations/devices/sync")
def batch_device_sync_webhook(
    sync_in: DeviceBatchSyncRequest,
    db: Session = Depends(get_db),
):
    """Batch ingestion endpoint for connected health cloud integrations."""
    return sync_connected_devices(db, [item.model_dump() for item in sync_in.items])
