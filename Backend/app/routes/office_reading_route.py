"""Office Readings API routes (Section 7c)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.office_reading_service import (
    record_office_reading,
    get_office_readings,
)
from app.schemas.office_reading import (
    OfficeReadingCreate,
    OfficeReadingOut,
)

router = APIRouter(tags=["office_readings"])


@router.post(
    "/doctor/patients/{id}/office-readings",
    response_model=OfficeReadingOut,
    status_code=status.HTTP_201_CREATED,
)
def doctor_record_office_reading(
    id: int,
    reading_in: OfficeReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Record office BP measurement; never analysed by the alert rules."""
    check_patient_access(current_user, id, db)
    return record_office_reading(
        db,
        patient_id=id,
        reading_in=reading_in,
        doctor_user_id=current_user.id,
    )


@router.get("/doctor/patients/{id}/office-readings", response_model=List[OfficeReadingOut])
def doctor_get_office_readings(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Office BP reading history."""
    check_patient_access(current_user, id, db)
    return get_office_readings(db, id)
