"""AI Clinical Summarization service (Section 23, RS-10)."""

from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.patientprofile import PatientProfile
from app.models.Alert import Alert
from app.models.BloodPressureReading import BloodPressureReading
from app.services.patient_service import get_doctor_pre_review_summary


def generate_patient_summary_draft(db: Session, patient_id: int) -> Dict[str, Any]:
    """Generate draft pre-review digest. Strictly marked as draft (RS-10)."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise ValueError("Patient not found")

    digest = get_doctor_pre_review_summary(db, patient_id)

    draft_text = (
        f"DRAFT SUMMARY - REQUIRES CLINICIAN VERIFICATION:\n"
        f"Patient {patient.first_name or ''} {patient.last_name or ''} ({patient.age_band or 'age unrecorded'}). "
        f"Target BP: {patient.target_systolic}/{patient.target_diastolic} mmHg. "
        f"Recent BP status shows adherence rate of {digest.get('adherence_rate', 'N/A')}%. "
        f"Active alerts: {len(digest.get('active_alerts', []))}. "
        f"722 protocol adherence: {'Met' if digest.get('cycle_completeness', {}).get('minimum_met') else 'Incomplete'}."
    )

    return {
        "is_draft": True,
        "requires_clinician_approval": True,
        "patient_id": patient_id,
        "draft_summary": draft_text,
        "clinical_digest_data": digest,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_alert_explanation_draft(db: Session, alert_id: int) -> Dict[str, Any]:
    """Generate plain-language alert explanation draft for patient communication."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise ValueError("Alert not found")

    tier_text = {
        "critical_emergency": "Très élevée nécessitant une attention urgente",
        "severe_single_reading": "Élevée sur une mesure isolée",
        "persistent_elevation": "Régulièrement au-dessus des objectifs fixés",
        "routine_out_of_range": "Légèrement hors cible",
    }.get(alert.tier, "Hors cible")

    explanation = (
        f"BROUILLON D'EXPLICATION AU PATIENT (À VALIDER PAR LE MÉDECIN) :\n"
        f"Bonjour. Votre dernière mesure de tension indique une valeur {tier_text}. "
        f"Votre médecin a été notifié. Merci de bien respecter le temps de repos avant toute nouvelle mesure "
        f"et de prendre vos médicaments prescrits comme convenu."
    )

    return {
        "is_draft": True,
        "requires_clinician_approval": True,
        "alert_id": alert_id,
        "patient_id": alert.patient_id,
        "draft_explanation": explanation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
