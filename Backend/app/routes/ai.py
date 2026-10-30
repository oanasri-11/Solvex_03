"""AI / clinical support routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai_summary import AISummaryResponse
from app.services.ai_summary_service import LLMSummaryError, generate_patient_summary
from app.services.assignment_service import is_doctor_assigned
from app.services.patient_context_service import build_patient_context
from app.services.patient_service import get_patient_profile_by_id

router = APIRouter(prefix="/ai", tags=["AI"])


class AISummaryRequest(BaseModel):
    period_days: int = Field(default=30, ge=1, le=365)


@router.post(
    "/patients/{patient_id}/summary",
    response_model=AISummaryResponse,
    tags=["AI"],
)
def generate_patient_summary_route(
    patient_id: int,
    request: AISummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate an AI summary for a hypertension patient (doctors only)."""
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can generate a patient summary",
        )

    patient = get_patient_profile_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    if not is_doctor_assigned(db, current_user.doctor_profile.id, patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This patient is not assigned to you",
        )

    try:
        patient_context = build_patient_context(db, patient_id, request.period_days)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    try:
        summary = generate_patient_summary(patient_context)
    except LLMSummaryError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        )

    return summary
