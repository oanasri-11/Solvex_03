<<<<<<< HEAD
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

=======
"""ScheduleSlot & Adherence API routes (Section 9)."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    get_current_patient,
    get_current_caregiver_or_patient,
    check_patient_access,
    resolve_acting_patient_id,
)
from app.models.user import User
from app.services.slot_service import (
    get_schedule_slots,
    get_schedule_slot_by_id,
    confirm_slot,
    doctor_confirm_slot,
    calculate_adherence,
)
from app.schemas.schedule_slot import (
    ScheduleSlotOut,
    SlotConfirmRequest,
)

router = APIRouter(tags=["schedule_slots"])


# ==========================================
# Patient / Caregiver Endpoints
# ==========================================

@router.get("/patients/me/schedule/slots", response_model=List[ScheduleSlotOut])
def get_own_slots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    status_filter: Optional[str] = Query(None, alias="status"),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Slots for acting patient (filters: from, to, status)."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="confirm_slot")
    return get_schedule_slots(
        db,
        patient_id=patient_id,
        from_date=from_date,
        to_date=to_date,
        status=status_filter,
    )


@router.get("/patients/me/schedule/slots/{id}", response_model=ScheduleSlotOut)
def get_own_slot_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Read a single slot for acting patient."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="confirm_slot")
    slot = get_schedule_slot_by_id(db, id)
    if not slot or slot.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")
    return slot


@router.post("/schedule-slots/{id}/confirm", response_model=ScheduleSlotOut)
def confirm_slot_route(
    id: int,
    confirm_in: SlotConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Close a slot (F15): taken=true with reading_ids or taken=false with reason."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="confirm_slot")
    slot = get_schedule_slot_by_id(db, id)
    if not slot or slot.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")

    try:
        return confirm_slot(
            db,
            slot_id=id,
            taken=confirm_in.taken,
            reading_ids=confirm_in.reading_ids,
            reason=confirm_in.reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/patients/me/adherence")
def get_own_adherence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
):
    """Adherence metrics for ?from&to."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return calculate_adherence(
        db,
        patient_id=current_user.patient_profile.id,
        from_date=from_date,
        to_date=to_date,
    )


# ==========================================
# Doctor Endpoints
# ==========================================

@router.post(
    "/doctor/patients/{id}/schedule-slots/{slot_id}/confirm",
    response_model=ScheduleSlotOut,
)
def doctor_confirm_patient_slot(
    id: int,
    slot_id: int,
    confirm_in: SlotConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Assisted slot confirmation by a clinician."""
    check_patient_access(current_user, id, db)
    try:
        return doctor_confirm_slot(
            db,
            patient_id=id,
            slot_id=slot_id,
            taken=confirm_in.taken,
            reading_ids=confirm_in.reading_ids,
            reason=confirm_in.reason,
            doctor_user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/doctor/patients/{id}/schedule/slots", response_model=List[ScheduleSlotOut])
def doctor_get_patient_slots(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Slots including missed and partial for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_schedule_slots(
        db,
        patient_id=id,
        from_date=from_date,
        to_date=to_date,
        status=status_filter,
    )


@router.get("/doctor/patients/{id}/adherence")
def doctor_get_patient_adherence(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
):
    """Adherence metrics for doctor view."""
    check_patient_access(current_user, id, db)
    return calculate_adherence(
        db,
        patient_id=id,
        from_date=from_date,
        to_date=to_date,
    )
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
