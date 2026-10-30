"""ReminderPreference API routes (Section 10)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_patient,
    get_current_caregiver_or_patient,
    resolve_acting_patient_id,
)
from app.models.user import User
from app.services.reminder_service import (
    get_reminder_preferences,
    replace_reminder_preferences,
    get_upcoming_reminders,
    register_push_token,
    remove_push_token,
)
from app.schemas.reminder import (
    ReminderPreferenceUpdate,
    ReminderPreferenceOut,
    PushTokenRequest,
    ReminderSlotOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(tags=["reminders"])


@router.get("/patients/me/reminder-preferences", response_model=ReminderPreferenceOut)
def get_own_reminder_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Settings and channels available to this patient."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    prefs = get_reminder_preferences(db, current_user.patient_profile.id)
    if not prefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")
    return prefs


@router.put("/patients/me/reminder-preferences", response_model=ReminderPreferenceOut)
def update_own_reminder_preferences(
    prefs_in: ReminderPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Replace reminder settings (422 outside configured windows)."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    # If SMS is selected, verify phone is verified
    if prefs_in.channel == "sms" and not current_user.phone_verified:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone must be verified before enabling SMS reminders",
        )

    return replace_reminder_preferences(db, current_user.patient_profile.id, prefs_in)


@router.get("/patients/me/reminders")
def get_upcoming_reminders_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Upcoming reminders with their slots."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="reminders")
    return get_upcoming_reminders(db, patient_id)


@router.put("/patients/me/push-tokens")
def register_push_token_route(
    req: PushTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Register or refresh a push token."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return register_push_token(
        db,
        patient_id=current_user.patient_profile.id,
        token=req.token,
        device_name=req.device_name,
    )


@router.delete("/patients/me/push-tokens/{id}", response_model=MessageResponse)
def remove_push_token_route(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Remove a push token."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    remove_push_token(db, current_user.patient_profile.id, id)
    return MessageResponse(message="Push token removed")
