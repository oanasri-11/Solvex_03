"""Consent service (Section 6, UCCONS, SC5)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.Consent import Consent
from app.models.patientprofile import PatientProfile


CURRENT_CONSENT_TEXTS = {
    "data_sharing": {
        "version": "1.0",
        "title_fr": "Partage des données de santé",
        "text_fr": "J'autorise le suivi et le partage de mes mesures tensionnelles avec mon équipe médicale.",
        "title_ar": "مشاركة البيانات الصحية",
        "text_ar": "أوافق على متابعة ومشاركة قياسات ضغط الدم مع فريقي الطبي.",
    },
    "monitoring_mode": {
        "version": "1.0",
        "title_fr": "Modalité de télésurveillance tensionnelle",
        "text_fr": "J'accepte le protocole de suivi tensionnel convenu avec mon médecin.",
        "title_ar": "طريقة المراقبة عن بعد",
        "text_ar": "أوافق على بروتوكول متابعة ضغط الدم المتفق عليه مع طبيبي.",
    },
    "caregiver_access": {
        "version": "1.0",
        "title_fr": "Accès pour aidant / proche",
        "text_fr": "J'autorise mon proche aidant à accéder à mes données et à saisir mes mesures.",
        "title_ar": "صلاحية الوصول للمرافق أو القريب",
        "text_ar": "أسمح للمرافق بالوصول إلى بياناتي والمساعدة في إدخال القياسات.",
    }
}


def get_current_consent_text() -> Dict[str, Any]:
    """Return current consent texts and versions in FR and AR."""
    return CURRENT_CONSENT_TEXTS


def record_consent(
    db: Session,
    patient_id: int,
    consent_type: str,
    text_version: str,
    accepted: bool = True,
    recorded_by: Optional[int] = None,
    method: str = "in_app",
    witness_note: Optional[str] = None,
) -> Consent:
    """Record consent (in_app, paper, or verbal)."""
    if consent_type not in ["data_sharing", "monitoring_mode", "caregiver_access"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid consent type '{consent_type}'")

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    consent = Consent(
        patient_id=patient_id,
        type=consent_type,
        text_version=text_version,
        accepted=accepted,
        accepted_at=datetime.now(timezone.utc),
        recorded_by=recorded_by,
        method=method,
        witness_note=witness_note,
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)

    # Check enrolment completion
    try:
        from app.services.patient_service import check_and_complete_enrolment
        check_and_complete_enrolment(db, patient_id)
    except Exception:
        pass

    return consent


def get_patient_consents(db: Session, patient_id: int) -> List[Consent]:
    """Get consent history for patient."""
    return db.query(Consent).filter(Consent.patient_id == patient_id).order_by(Consent.accepted_at.desc()).all()


def get_effective_consent_state(db: Session, patient_id: int) -> Dict[str, Any]:
    """Return effective active consent per type."""
    consents = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.withdrawn_at.is_(None)
    ).all()

    state = {
        "data_sharing": False,
        "monitoring_mode": False,
        "caregiver_access": False,
    }
    for c in consents:
        if c.type in state:
            state[c.type] = c.accepted

    return state


def withdraw_consent(
    db: Session,
    consent_id: int,
    patient_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Consent:
    if patient_id is None and user_id is not None:
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        patient_id = user.patient_profile.id if user and user.patient_profile else user_id
    patient_id = patient_id or 1
    """Withdraw a consent. Flags case for doctor; no automatic deletion."""
    consent = db.query(Consent).filter(
        Consent.id == consent_id,
        Consent.patient_id == patient_id
    ).first()
    if not consent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent record not found")

    consent.withdrawn_at = datetime.now(timezone.utc)
    consent.accepted = False
    db.commit()
    db.refresh(consent)

    # Recalculate priority
    try:
        from app.services.priority_service import calculate_patient_priority
        calculate_patient_priority(db, patient_id)
    except Exception:
        pass

    return consent
