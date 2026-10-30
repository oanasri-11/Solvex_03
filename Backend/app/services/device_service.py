"""Connected Devices & Low-Bandwidth Integrations service (Section 11b)."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import re
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.ConnectedDevice import ConnectedDevice
from app.models.patientprofile import PatientProfile
from app.models.user import User
from app.models.BloodPressureReading import BloodPressureReading
from app.services.reading_service import create_blood_pressure_reading


def get_patient_devices(db: Session, patient_id: int) -> List[ConnectedDevice]:
    """List paired blood pressure monitors for a patient."""
    return db.query(ConnectedDevice).filter(ConnectedDevice.patient_id == patient_id).all()


def pair_device(
    db: Session,
    patient_id: int,
    device_data: Any,
) -> ConnectedDevice:
    """Pair a Bluetooth/BLE home monitor."""
    data = device_data.model_dump(exclude_unset=True) if hasattr(device_data, "model_dump") else dict(device_data)
    device = ConnectedDevice(
        patient_id=patient_id,
        device_model=data.get("device_model", "Standard BLE Monitor"),
        serial_number=data.get("serial_number"),
        mac_address=data.get("mac_address"),
        validation_status=data.get("validation_status", "stride_bp_validated"),
        paired_at=datetime.now(timezone.utc),
    )
    try:
        db.add(device)
        db.commit()
        db.refresh(device)
        return device
    except SQLAlchemyError:
        db.rollback()
        raise


def unpair_device(
    db: Session,
    patient_id: int,
    device_id: int,
) -> bool:
    """Unpair a device."""
    device = (
        db.query(ConnectedDevice)
        .filter(ConnectedDevice.id == device_id, ConnectedDevice.patient_id == patient_id)
        .first()
    )
    if not device:
        return False
    try:
        db.delete(device)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        raise


def process_inbound_sms(
    db: Session,
    sender_phone: str,
    message_text: str,
    source_message_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse structured text replies from SMS (e.g. '130/80 72') and save reading.
    
    Format: '<systolic>/<diastolic> [pulse]' or '<systolic> <diastolic> [pulse]'
    """
    # 1. Identify patient by verified phone
    user = db.query(User).filter(User.phone == sender_phone, User.phone_verified == True).first()
    if not user or not user.patient_profile:
        raise ValueError("Sender phone number not recognized or phone not verified")

    patient_id = user.patient_profile.id

    # 2. Parse reading
    match = re.search(r"(\d{2,3})\s*[/,\s]\s*(\d{2,3})(?:\s+(\d{2,3}))?", message_text.strip())
    if not match:
        raise ValueError("Invalid SMS reading format. Expected: '130/80' or '130/80 72'")

    sbp = int(match.group(1))
    dbp = int(match.group(2))
    pulse = int(match.group(3)) if match.group(3) else None

    # 3. Create reading via reading_service
    reading_payload = {
        "patient_id": patient_id,
        "systolic": sbp,
        "diastolic": dbp,
        "pulse": pulse,
        "measured_at": datetime.now(timezone.utc),
        "capture_method": "low_bandwidth_sms",
        "entered_by": "patient",
        "actor_id": user.id,
    }

    reading = create_blood_pressure_reading(db, reading_payload, actor_user=user)
    return {
        "status": "success",
        "reading_id": reading.id if reading else None,
        "systolic": sbp,
        "diastolic": dbp,
        "pulse": pulse,
        "patient_id": patient_id,
    }


def sync_connected_devices(
    db: Session,
    sync_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Batch ingestion for connected health cloud integrations."""
    ingested = 0
    errors = []

    for rec in sync_records:
        try:
            device_record_id = rec.get("device_record_id")
            patient_id = rec.get("patient_id")
            if not patient_id:
                continue

            sbp = rec.get("systolic")
            dbp = rec.get("diastolic")
            pulse = rec.get("pulse")
            measured_at_str = rec.get("measured_at")
            measured_at = (
                datetime.fromisoformat(measured_at_str)
                if measured_at_str
                else datetime.now(timezone.utc)
            )

            reading_payload = {
                "patient_id": patient_id,
                "systolic": sbp,
                "diastolic": dbp,
                "pulse": pulse,
                "measured_at": measured_at,
                "capture_method": "connected_device",
                "entered_by": "device",
            }
            create_blood_pressure_reading(db, reading_payload)
            ingested += 1
        except Exception as e:
            errors.append({"record": rec, "error": str(e)})

    return {"ingested_count": ingested, "errors": errors}
