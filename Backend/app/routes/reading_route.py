<<<<<<< HEAD
"""Blood pressure reading routes.

Route -> Service Layer -> CRUD (SQLAlchemy) -> Database.
Readings are immutable: only CREATE and GET are exposed; corrections create a new
reading referencing the original via recheck_of_reading_id.
Access control: patients only their own readings; doctors only assigned patients;
admins full access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
=======
"""BloodPressureReading API routes (Section 11)."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query, Response
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
<<<<<<< HEAD
    get_current_admin,
    get_current_doctor,
    get_current_patient,
    check_patient_access,
=======
    get_current_doctor,
    get_current_patient,
    get_current_caregiver_or_patient,
    check_patient_access,
    resolve_acting_patient_id,
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
)
from app.models.user import User
from app.services.reading_service import (
    create_blood_pressure_reading,
<<<<<<< HEAD
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

=======
    get_all_blood_pressure_readings,
    get_blood_pressure_reading_by_id,
    confirm_reading,
    annotate_reading,
    get_patient_trends,
    get_doctor_trends,
)
from app.schemas.measurement import (
    BloodPressureReadingCreate,
    BloodPressureReadingOut,
    ReadingConfirmRequest,
    ReadingAnnotateRequest,
)

router = APIRouter(tags=["readings"])


# ==========================================
# Ingestion Endpoints (Idempotency-Key required)
# ==========================================

@router.post("/readings", response_model=BloodPressureReadingOut, status_code=status.HTTP_201_CREATED)
def patient_create_reading(
    reading_in: BloodPressureReadingCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Primary ingestion call: verifies, saves, links session/slot, evaluates trends, generates alerts, updates priority."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="record")

    # Set entered_by and actor
    entered_by = "caregiver" if current_user.role == "caregiver" else "patient"

    payload = reading_in.model_dump()
    payload["patient_id"] = patient_id
    payload["entered_by"] = entered_by
    payload["actor_id"] = current_user.id

    try:
        reading = create_blood_pressure_reading(db, payload, actor_user=current_user)
        if not reading:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="READING_REJECTED")
        return reading
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/doctor/patients/{id}/readings",
    response_model=BloodPressureReadingOut,
    status_code=status.HTTP_201_CREATED,
)
def doctor_assisted_entry(
    id: int,
    reading_in: BloodPressureReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """Assisted measurement entry by assigned clinician."""
    check_patient_access(current_user, id, db)

    payload = reading_in.model_dump()
    payload["patient_id"] = id
    payload["entered_by"] = "professional"
    payload["actor_id"] = current_user.id
    payload["capture_method"] = "assisted"

    try:
        reading = create_blood_pressure_reading(db, payload, actor_user=current_user)
        if not reading:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="READING_REJECTED")
        return reading
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ==========================================
# History & Reading Details
# ==========================================

@router.get("/patients/me/readings", response_model=List[BloodPressureReadingOut])
def get_own_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    verification_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Patient reading history (filters: from, to, verification_status, page)."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="view_history")
    skip = (page - 1) * page_size
    readings = get_all_blood_pressure_readings(
        db,
        patient_id=patient_id,
        from_date=from_date,
        to_date=to_date,
        verification_status=verification_status,
        skip=skip,
        limit=page_size,
    )
    # Hide doctor-only data_quality_flags for patient view
    for r in readings:
        r.data_quality_flags = None
    return readings


@router.get("/readings/{id}", response_model=BloodPressureReadingOut)
def get_reading_by_id_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Single reading details."""
    reading = get_blood_pressure_reading_by_id(db, id)
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")

    check_patient_access(current_user, reading.patient_id, db)
    # If not doctor/admin, hide data_quality_flags
    if current_user.role not in ("doctor", "admin"):
        reading.data_quality_flags = None
    return reading


@router.post("/readings/{id}/confirm", response_model=BloodPressureReadingOut)
def confirm_unusual_reading(
    id: int,
    confirm_in: ReadingConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Confirm an unusual value (needs_confirmation -> confirmed_by_entrant); triggers re-analysis."""
    reading = get_blood_pressure_reading_by_id(db, id)
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")

    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="confirm_slot")
    if reading.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return confirm_reading(db, id, note=confirm_in.note)


@router.post("/readings/{id}/annotate", response_model=BloodPressureReadingOut)
def annotate_reading_route(
    id: int,
    annotate_in: ReadingAnnotateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add non-clinical entrant note or contextual tag."""
    reading = get_blood_pressure_reading_by_id(db, id)
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")

    check_patient_access(current_user, reading.patient_id, db)
    return annotate_reading(db, id, note=annotate_in.note, tags=annotate_in.tags)


# ==========================================
# Trend Views
# ==========================================

@router.get("/patients/me/trends")
def get_own_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_caregiver_or_patient),
    range_param: str = Query("30d", alias="range", description="7d, 30d, 90d"),
    x_acting_for: Optional[int] = Header(None, alias="X-Acting-For"),
):
    """Patient trend chart data: session averages, target band, protocol cycle markers."""
    patient_id = resolve_acting_patient_id(current_user, db, x_acting_for, required_scope="view_trend")
    return get_patient_trends(db, patient_id, time_range=range_param)


@router.get("/doctor/patients/{id}/readings", response_model=List[BloodPressureReadingOut])
def doctor_get_patient_readings(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    verification_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Audit-grade reading log with data_quality_flags, entered_by, actor_id, received_at."""
    check_patient_access(current_user, id, db)
    skip = (page - 1) * page_size
    return get_all_blood_pressure_readings(
        db,
        patient_id=id,
        from_date=from_date,
        to_date=to_date,
        verification_status=verification_status,
        skip=skip,
        limit=page_size,
    )


@router.get("/doctor/patients/{id}/trends")
def doctor_get_patient_trends(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
    range_param: str = Query("30d", alias="range"),
):
    """Doctor trend view with medication event overlays, alert markers, office BP points."""
    check_patient_access(current_user, id, db)
    return get_doctor_trends(db, id, time_range=range_param)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
