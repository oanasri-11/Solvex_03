"""Reports & Exports service (Section 20)."""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.patientprofile import PatientProfile
from app.models.BloodPressureReading import BloodPressureReading
from app.models.TreatmentEvent import TreatmentEvent
from app.models.OfficeReading import OfficeReading
from app.models.Alert import Alert
from app.services.patient_service import get_patient_summary


# In-memory export job tracker for SQLite environment
EXPORT_JOBS: Dict[str, Dict[str, Any]] = {}


def preview_patient_report(db: Session, patient_id: int) -> Dict[str, Any]:
    """Preview structured clinical report content (RS-9)."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise ValueError("Patient not found")

    summary = get_patient_summary(db, patient_id)

    readings = (
        db.query(BloodPressureReading)
        .filter(BloodPressureReading.patient_id == patient_id)
        .order_by(BloodPressureReading.measured_at.desc())
        .limit(50)
        .all()
    )

    treatments = (
        db.query(TreatmentEvent)
        .filter(TreatmentEvent.patient_id == patient_id)
        .order_by(TreatmentEvent.effective_date.desc())
        .all()
    )

    office_readings = (
        db.query(OfficeReading)
        .filter(OfficeReading.patient_id == patient_id)
        .order_by(OfficeReading.measured_at.desc())
        .all()
    )

    alerts = (
        db.query(Alert)
        .filter(Alert.patient_id == patient_id)
        .order_by(Alert.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "patient": {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age_band": patient.age_band,
            "target": f"{patient.target_systolic}/{patient.target_diastolic}",
        },
        "summary": summary,
        "recent_readings_count": len(readings),
        "treatment_events": [
            {
                "date": str(t.effective_date),
                "type": t.event_type,
                "drug": t.drug_name,
                "dose": t.dose,
                "class": t.drug_class,
            }
            for t in treatments
        ],
        "office_readings": [
            {
                "measured_at": str(o.measured_at),
                "bp": f"{o.systolic}/{o.diastolic}",
                "note": o.note,
            }
            for o in office_readings
        ],
        "recent_alerts_count": len(alerts),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def start_report_export(
    db: Session,
    patient_id: int,
    format: str = "pdf",
) -> Dict[str, Any]:
    """Start asynchronous formal report export job."""
    job_id = str(uuid.uuid4())
    EXPORT_JOBS[job_id] = {
        "job_id": job_id,
        "patient_id": patient_id,
        "format": format.lower(),
        "status": "completed",  # Complete immediately in-process
        "download_url": f"/api/v1/doctor/reports/{job_id}/download",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {
        "job_id": job_id,
        "status": "completed",
        "download_url": EXPORT_JOBS[job_id]["download_url"],
    }


def get_export_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Poll export job status."""
    return EXPORT_JOBS.get(job_id)
