"""System Config, Localized Content & Guidelines API routes (Section 15)."""

from typing import Optional
from fastapi import APIRouter, Header

from app.services.config_service import (
    get_patient_content,
    get_labels,
    get_features,
)
from app.schemas.config import (
    PatientContentResponse,
    LabelsResponse,
    FeaturesResponse,
)

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/patient-content", response_model=PatientContentResponse)
def get_patient_content_route(
    lang: Optional[str] = Header("fr", alias="Accept-Language"),
):
    """Emergency guidance texts, emergency phone numbers (14 / 1021 in Algeria), red-flag symptom screens in FR/AR."""
    return get_patient_content(lang=lang or "fr")


@router.get("/labels", response_model=LabelsResponse)
def get_labels_route(
    lang: Optional[str] = Header("fr", alias="Accept-Language"),
):
    """Status labels, alert tier names, data-quality warning strings, priority reason codes."""
    return get_labels(lang=lang or "fr")


@router.get("/features", response_model=FeaturesResponse)
def get_features_route():
    """Operational feature flags (flag.low_bandwidth_channel, flag.caregiver_assisted_entry, flag.office_readings)."""
    return FeaturesResponse(features=get_features())
