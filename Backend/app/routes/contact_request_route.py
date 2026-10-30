

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.patient_service import get_patient_profile_by_user_id

from app.services.contact_request_service import (
    create_contact_request,
    get_contact_request_by_id,
    get_all_contact_requests,
    update_contact_request,
    complete_contact_request,
)

from app.services.assignment_service import (
    is_doctor_assigned,
)

from app.schemas.contact_request import (
    ContactRequestCreate,
    ContactRequestUpdate,
    ContactRequestOut,
)

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore


router = APIRouter(
    prefix="/contact-requests",
    tags=["Contact Requests"],
)


# Helper: Check patient access
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
                detail="You can only access your own contact requests",
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
                detail="Contact request not found or patient not assigned",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# Helper: Check contact request access
def _require_contact_request_access(
    current_user: User,
    contact_request,
    db: Session,
):
    _require_patient_access(
        current_user,
        contact_request.patient_id,
        db,
    )


# 1. Create contact request (doctor only)
@router.post(
    "/",
    response_model=ContactRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def create_contact_request_route(
    request_in: ContactRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create contact requests",
        )

    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    _require_patient_access(
        current_user,
        request_in.patient_id,
        db,
    )

    request_data = request_in.model_copy(
        update={"doctor_id": current_user.doctor_profile.id}
    )

    contact_request = create_contact_request(
        db,
        request_data,
    )

    if not contact_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return contact_request


# 2. List contact requests
@router.get("/", response_model=List[ContactRequestOut])
def list_contact_requests(
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

        # Ignore any patient_id supplied by the client.
        return get_all_contact_requests(
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

        requests = get_all_contact_requests(
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
        detail="Not authorized to view contact requests",
    )


# 3. Get contact request by ID
@router.get("/{request_id}", response_model=ContactRequestOut)
def get_contact_request_route(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    contact_request = get_contact_request_by_id(
        db,
        request_id,
    )

    if not contact_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found",
        )

    _require_contact_request_access(
        current_user,
        contact_request,
        db,
    )

    return contact_request


# 4. Update contact request (doctor only)
@router.put("/{request_id}", response_model=ContactRequestOut)
def update_contact_request_route(
    request_id: int,
    request_in: ContactRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update contact requests",
        )

    contact_request = get_contact_request_by_id(
        db,
        request_id,
    )

    if not contact_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found",
        )

    _require_contact_request_access(
        current_user,
        contact_request,
        db,
    )

    updated = update_contact_request(
        db,
        request_id,
        request_in,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found",
        )

    return updated


# 5. Complete contact request (doctor only)
@router.post(
    "/{request_id}/complete",
    response_model=ContactRequestOut,
)
def complete_contact_request_route(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can complete contact requests",
        )

    contact_request = get_contact_request_by_id(
        db,
        request_id,
    )

    if not contact_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found",
        )

    _require_contact_request_access(
        current_user,
        contact_request,
        db,
    )

    completed = complete_contact_request(
        db,
        request_id,
    )

    if not completed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found",
        )

    return completed
