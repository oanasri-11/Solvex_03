"""Schedule slot routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Slots are system-generated; clients only confirm/close a slot. A slot cannot be
confirmed twice. No client-side DELETE.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_active_user, get_current_admin, get_current_doctor
from app.models.user import User
from app.services.slot_service import (
    create_schedule_slot,
    get_schedule_slot_by_id,
    get_all_schedule_slots,
    update_schedule_slot,
)
from app.schemas.schedule_slot import (
    ScheduleSlotCreate,
    ScheduleSlotUpdate,
    ScheduleSlotOut,
)

router = APIRouter(prefix="/slots", tags=["slots"])


def _require_doctor_or_admin(current_user: User) -> None:
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )


@router.get("/", response_model=List[ScheduleSlotOut])
def list_slots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    schedule_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
):
    """List schedule slots."""
    return get_all_schedule_slots(
        db, skip=skip, limit=limit, schedule_id=schedule_id, status=status
    )


@router.get("/{slot_id}", response_model=ScheduleSlotOut)
def get_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a schedule slot by ID."""
    slot = get_schedule_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found"
        )
    return slot


@router.post(
    "/",
    response_model=ScheduleSlotOut,
    status_code=status.HTTP_201_CREATED,
)
def create_slot_route(
    slot_in: ScheduleSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a schedule slot (system-generated; doctors/admins only)."""
    _require_doctor_or_admin(current_user)
    slot = create_schedule_slot(db, slot_in)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return slot


@router.put("/{slot_id}", response_model=ScheduleSlotOut)
def update_slot_route(
    slot_id: int,
    slot_in: ScheduleSlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a slot (confirm/close). Fails if already closed."""
    slot = get_schedule_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found"
        )
    updated = update_schedule_slot(db, slot_id, slot_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot cannot be confirmed twice or not found",
        )
    return updated

