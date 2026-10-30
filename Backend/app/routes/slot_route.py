
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.slot_service import (
    get_schedule_slot_by_id,
    get_all_schedule_slots,
    update_schedule_slot,
)

from app.services.patient_service import (
    get_patient_profile_by_user_id,
)

from app.services.assignment_service import (
    is_doctor_assigned,
    get_all_assignments,
)

from app.schemas.schedule_slot import (
    ScheduleSlotUpdate,
    ScheduleSlotOut,
)


router = APIRouter(
    prefix="/slots",
    tags=["Schedule Slots"],
)


# Helper: Check access to a slot
def _require_slot_access(
    current_user: User,
    slot,
    db: Session,
) -> None:

    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile or profile.id != slot.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another patient's slot",
            )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        if not is_doctor_assigned(
            db,
            current_user.doctor_profile.id,
            slot.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found or patient not assigned to doctor",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# 1. List accessible schedule slots
@router.get("/", response_model=List[ScheduleSlotOut])
def list_slots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    schedule_id: Optional[int] = Query(None),
    slot_status: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile:
            return []

        slots = get_all_schedule_slots(
            db,
            skip=skip,
            limit=limit,
            schedule_id=schedule_id,
            status=slot_status,
        )

        return [
            slot for slot in slots
            if slot.patient_id == profile.id
        ]

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        assignments = get_all_assignments(
            db,
            doctor_id=current_user.doctor_profile.id,
            active=True,
        )

        allowed_patient_ids = {
            assignment.patient_id for assignment in assignments
        }

        slots = get_all_schedule_slots(
            db,
            skip=0,
            limit=10000,
            schedule_id=schedule_id,
            status=slot_status,
        )

        accessible_slots = [
            slot for slot in slots
            if slot.patient_id in allowed_patient_ids
        ]

        return accessible_slots[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to list schedule slots",
    )


# 2. Get slot by ID
@router.get("/{slot_id}", response_model=ScheduleSlotOut)
def get_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    slot = get_schedule_slot_by_id(
        db,
        slot_id,
    )

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )

    _require_slot_access(
        current_user,
        slot,
        db,
    )

    return slot


# 3. Confirm a schedule slot
@router.post(
    "/{slot_id}/confirm",
    response_model=ScheduleSlotOut,
)
def confirm_slot_route(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "patient":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can confirm their own schedule slots",
        )

    slot = get_schedule_slot_by_id(
        db,
        slot_id,
    )

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )

    _require_slot_access(
        current_user,
        slot,
        db,
    )

    if slot.status != "PENDING":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This slot has already been completed or closed",
        )

    slot_update = ScheduleSlotUpdate(
        status="COMPLETED",
    )

    updated = update_schedule_slot(
        db,
        slot_id,
        slot_update,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot could not be confirmed",
        )

    return updated


