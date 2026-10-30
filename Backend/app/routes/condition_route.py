<<<<<<< HEAD

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
=======
"""Clinical Conditions API routes (Section 7)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
<<<<<<< HEAD
    check_patient_access,
)
from app.models.user import User

from app.services.patient_service import get_patient_profile_by_user_id
from app.services.condition_service import (
    create_patient_condition,
    get_patient_condition_by_id,
    get_all_patient_conditions,
    update_patient_condition,
    delete_patient_condition,
)
from app.services.assignment_service import (
    is_doctor_assigned,
    get_all_assignments,
)

=======
    get_current_doctor,
    get_current_patient,
    check_patient_access,
)
from app.models.user import User
from app.services.condition_service import (
    create_patient_condition,
    get_patient_conditions,
    get_patient_condition_by_id,
    update_patient_condition,
    delete_patient_condition,
)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from app.schemas.condition import (
    PatientConditionCreate,
    PatientConditionUpdate,
    PatientConditionOut,
)
<<<<<<< HEAD


router = APIRouter(prefix="/conditions", tags=["Conditions"])


# Helper: Get patient profile for the authenticated patient
def _patient_profile_for(db: Session, current_user: User):
    if current_user.role == "patient":# type: ignore
        return get_patient_profile_by_user_id(db, current_user.id)# type: ignore

    return None


# Helper: Check whether the current user can access a condition
def _require_condition_access(
    current_user: User,
    condition,
    db: Session,
) -> None:

    if current_user.role == "patient":# type: ignore
        check_patient_access(current_user, condition.patient_id, db)

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        if not is_doctor_assigned(
            db,
            current_user.doctor_profile.id,
            condition.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access patient conditions",
        )


# 1. List conditions
@router.get("/", response_model=List[PatientConditionOut])
def list_conditions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    conditions = get_all_patient_conditions(
        db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        is_active=is_active,
    )

    if current_user.role == "patient":# type: ignore
        profile = _patient_profile_for(db, current_user)

        if not profile:
            return []

        conditions = [
            condition
            for condition in conditions
            if condition.patient_id == profile.id# type: ignore
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

        conditions = [
            condition
            for condition in conditions
            if condition.patient_id in allowed_patient_ids
        ]

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access patient conditions",
        )

    return conditions


# 2. Create condition
@router.post(
    "/",
    response_model=PatientConditionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_condition_route(
    condition_in: PatientConditionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a condition for a patient."""

    if current_user.role == "patient":# type: ignore
        profile = _patient_profile_for(db, current_user)

        if not profile or condition_in.patient_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients may only add conditions for themselves",
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
            condition_in.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor is not assigned to this patient",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create patient conditions",
        )

    condition = create_patient_condition(db, condition_in)

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return condition


# 3. Update condition
@router.put("/{condition_id}", response_model=PatientConditionOut)
def update_condition_route(
    condition_id: int,
    condition_in: PatientConditionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a patient condition."""

    condition = get_patient_condition_by_id(db, condition_id)

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found",
        )

    _require_condition_access(current_user, condition, db)

    updated = update_patient_condition(db, condition_id, condition_in)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found",
        )

    return updated


# 4. Soft-delete condition
@router.post("/{condition_id}/delete", response_model=PatientConditionOut)
def delete_condition_route(
    condition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Soft-delete a patient condition (is_active = False)."""

    condition = get_patient_condition_by_id(db, condition_id)

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found",
        )

    _require_condition_access(current_user, condition, db)

    deleted = delete_patient_condition(db, condition_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found",
        )

    return deleted


# 5. Get condition by ID
@router.get("/{condition_id}", response_model=PatientConditionOut)
def get_condition(
    condition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a patient condition by ID."""

    condition = get_patient_condition_by_id(db, condition_id)

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found",
        )

    _require_condition_access(current_user, condition, db)

    return condition


=======
from app.schemas.common import MessageResponse

router = APIRouter(tags=["conditions"])


@router.post("/doctor/patients/{id}/conditions", response_model=PatientConditionOut, status_code=status.HTTP_201_CREATED)
def doctor_add_condition(
    id: int,
    condition_in: PatientConditionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Add a coded condition; recalculates priority and target suggestion."""
    check_patient_access(current_user, id, db)
    return create_patient_condition(
        db,
        patient_id=id,
        condition_in=condition_in,
        recorded_by=current_user.id,
    )


@router.get("/doctor/patients/{id}/conditions", response_model=List[PatientConditionOut])
def doctor_list_conditions(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """List clinical conditions for assigned patient."""
    check_patient_access(current_user, id, db)
    return get_patient_conditions(db, id)


@router.get("/patients/me/conditions", response_model=List[PatientConditionOut])
def patient_get_conditions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient),
):
    """Read-only 'Health context' for the patient."""
    if not current_user.patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return get_patient_conditions(db, current_user.patient_profile.id)


@router.patch("/conditions/{id}", response_model=PatientConditionOut)
def doctor_update_condition(
    id: int,
    condition_in: PatientConditionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Update detail or deactivate a condition."""
    cond = get_patient_condition_by_id(db, id)
    if not cond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    check_patient_access(current_user, cond.patient_id, db)
    return update_patient_condition(db, id, condition_in)


@router.delete("/conditions/{id}", response_model=MessageResponse)
def doctor_delete_condition(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Soft delete clinical condition."""
    cond = get_patient_condition_by_id(db, id)
    if not cond:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")
    check_patient_access(current_user, cond.patient_id, db)
    delete_patient_condition(db, id)
    return MessageResponse(message=f"Condition {id} deactivated")
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
