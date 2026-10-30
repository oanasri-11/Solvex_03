"""Blood pressure reading routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Readings are immutable: only CREATE and GET are exposed; corrections create a new
reading referencing the original via recheck_of_reading_id.
Access control: patients only their own readings; doctors only assigned patients;
admins full access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.reading_service import (
    create_blood_pressure_reading,
    get_blood_pressure_reading_by_id,
    get_all_blood_pressure_readings,
)
from app.services.patient_service import get_patient_profile_by_user_id
from app.schemas.measurement import (
    BloodPressureReadingCreate,
    BloodPressureReadingUpdate,
    BloodPressureReadingOut,
)

router = APIRouter(prefix="/readings", tags=["readings"])


def _require_reading_access(current_user: User, reading, db: Session) -> None:
    if current_user.role == "patient":# type: ignore
        check_patient_access(current_user, reading.patient_id, db)
    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import is_doctor_assigned

        if not is_doctor_assigned(db, current_user.doctor_profile.id, reading.patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )


@router.get("/", response_model=List[BloodPressureReadingOut])
def list_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
):
    """List blood pressure readings."""
    readings = get_all_blood_pressure_readings(
        db, skip=skip, limit=limit, patient_id=patient_id
    )
    if current_user.role == "patient":# type: ignore
        profile = (
            __import__("app.services.patient_service", fromlist=["get_patient_profile_by_user_id"]).get_patient_profile_by_user_id(
                db, current_user.id
            )
        )
        if not profile:
            return []
        readings = [r for r in readings if r.patient_id == profile.id]
    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found"
            )
        from app.services.assignment_service import get_all_assignments

        assignments = get_all_assignments(
            db, doctor_id=current_user.doctor_profile.id, active=True
        )
        allowed_patient_ids = {a.patient_id for a in assignments}
        readings = [r for r in readings if r.patient_id in allowed_patient_ids]
    return readings


@router.get("/{reading_id}", response_model=BloodPressureReadingOut)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a blood pressure reading by ID."""
    reading = get_blood_pressure_reading_by_id(db, reading_id)
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found"
        )
    _require_reading_access(current_user, reading, db)
    return reading


@router.post(
    "/",
    response_model=BloodPressureReadingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_reading_route(
    reading_in: BloodPressureReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a blood pressure reading."""
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(db, current_user.id)# type: ignore
        if not profile or reading_in.patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients may only create readings for themselves",
            )
    reading = create_blood_pressure_reading(db, reading_in)
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return reading

