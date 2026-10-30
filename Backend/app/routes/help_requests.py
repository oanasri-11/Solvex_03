
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.patient_service import get_patient_profile_by_user_id
from app.services.assignment_service import is_doctor_assigned

from app.services.help_request_service import (
    create_patient_help_request,
    get_patient_help_request_by_id,
    get_all_patient_help_requests,
    cancel_patient_help_request,
)

from app.schemas.help_request import (
    PatientHelpRequestCreate,
    PatientHelpRequestOut,
)

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore


router = APIRouter(
    prefix="/help-requests",
    tags=["Patient Help Requests"],
)


# Helper: Check access to a patient's help requests
def _require_patient_access(
    current_user: User,
    patient_id: int,
    db: Session,
):
    if current_user.role == "patient":# type: ignore
        profile = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not profile or profile.id != patient_id:# type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own help requests",
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
            patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Help request not found or patient not assigned",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# Helper: Check access to a help request
def _require_help_request_access(
    current_user: User,
    help_request,
    db: Session,
):
    _require_patient_access(
        current_user,
        help_request.patient_id,
        db,
    )


# 1. Create help request (patient only)
@router.post(
    "/",
    response_model=PatientHelpRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_help_request_route(
    request_in: PatientHelpRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "patient":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can submit help requests",
        )

    profile = get_patient_profile_by_user_id(
        db,
        current_user.id,# type: ignore
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )

    # Do not trust patient_id supplied by the client.
    request_data = request_in.model_copy(
        update={"patient_id": profile.id}
    )

    help_request = create_patient_help_request(
        db,
        request_data,
    )

    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return help_request


# 2. List help requests
@router.get("/", response_model=List[PatientHelpRequestOut])
def list_help_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    request_status: Optional[str] = Query(None, alias="status"),
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

        # Ignore patient_id supplied by the client.
        return get_all_patient_help_requests(
            db,
            skip=skip,
            limit=limit,
            patient_id=profile.id,# type: ignore
            status=request_status,
        )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        requests = get_all_patient_help_requests(
            db,
            skip=0,
            limit=10000,
            patient_id=patient_id,
            status=request_status,
        )

        allowed_requests = []

        for request in requests:
            if is_doctor_assigned(
                db,
                current_user.doctor_profile.id,
                request.patient_id,# type: ignore
            ):
                allowed_requests.append(request)

        return allowed_requests[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to view help requests",
    )


# 3. Get help request by ID
@router.get("/{request_id}", response_model=PatientHelpRequestOut)
def get_help_request_route(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    help_request = get_patient_help_request_by_id(
        db,
        request_id,
    )

    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found",
        )

    _require_help_request_access(
        current_user,
        help_request,
        db,
    )

    return help_request


# 4. Cancel help request (patient only)
@router.post(
    "/{request_id}/cancel",
    response_model=PatientHelpRequestOut,
)
def cancel_help_request_route(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "patient":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can cancel their help requests",
        )

    help_request = get_patient_help_request_by_id(
        db,
        request_id,
    )

    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found",
        )

    _require_help_request_access(
        current_user,
        help_request,
        db,
    )

    canceled = cancel_patient_help_request(
        db,
        request_id,
    )

    if not canceled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This help request cannot be canceled",
        )

    return canceled
