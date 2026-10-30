"""AI Clinical Summarization API routes (Section 23, RS-10)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.ai_service import (
    generate_patient_summary_draft,
    generate_alert_explanation_draft,
)
from app.schemas.ai import (
    AISummaryResponse,
    AIAlertExplanationResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/patients/{id}/summary", response_model=AISummaryResponse)
def generate_patient_summary_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Generate draft pre-review digest (strictly marked draft; clinician approval required)."""
    check_patient_access(current_user, id, db)
    try:
        return generate_patient_summary_draft(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/alerts/{id}/explanation", response_model=AIAlertExplanationResponse)
def generate_alert_explanation_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Generate plain-language alert explanation draft for patient communication."""
    try:
        return generate_alert_explanation_draft(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
