
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

from app.services.follow_up_action_service import (
    create_follow_up_action,
    get_follow_up_action_by_id,
    get_all_follow_up_actions,
    update_follow_up_action,
    complete_follow_up_action,
)

from app.services.assignment_service import is_doctor_assigned
from app.services.patient_service import get_patient_profile_by_user_id

from app.schemas.follow_up import (
    FollowUpActionCreate,
    FollowUpActionUpdate,
    FollowUpActionOut,
)

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore


router = APIRouter(
    prefix="/follow-up-actions",
    tags=["Follow-up Actions"],
)


# Helper: Check access to a patient's actions
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
                detail="You can only access your own follow-up actions",
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
                detail="Follow-up action not found or patient not assigned",
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


# Helper: Check access to a follow-up action
def _require_action_access(
    current_user: User,
    action,
    db: Session,
):
    _require_patient_access(
        current_user,
        action.patient_id,
        db,
    )


# 1. Create follow-up action (doctor only)
@router.post(
    "/",
    response_model=FollowUpActionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_follow_up_action_route(
    action_in: FollowUpActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create follow-up actions",
        )

    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    _require_patient_access(
        current_user,
        action_in.patient_id,
        db,
    )

    # Do not trust a doctor_id supplied by the client.
    action_data = action_in.model_copy(
        update={"doctor_id": current_user.doctor_profile.id}
    )

    action = create_follow_up_action(
        db,
        action_data,
    )

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return action


# 2. List follow-up actions
@router.get("/", response_model=List[FollowUpActionOut])
def list_follow_up_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    patient_id: Optional[int] = Query(None),
    action_status: Optional[str] = Query(None, alias="status"),
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
        return get_all_follow_up_actions(
            db,
            skip=skip,
            limit=limit,
            patient_id=profile.id,# type: ignore
            status=action_status,
        )

    elif current_user.role == "doctor":# type: ignore
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        actions = get_all_follow_up_actions(
            db,
            skip=0,
            limit=10000,
            patient_id=patient_id,
            status=action_status,
        )

        allowed_actions = []

        for action in actions:
            if is_doctor_assigned(
                db,
                current_user.doctor_profile.id,
                action.patient_id,# type: ignore
            ):
                allowed_actions.append(action)

        return allowed_actions[skip:skip + limit]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to view follow-up actions",
    )


# 3. Get follow-up action by ID
@router.get("/{action_id}", response_model=FollowUpActionOut)
def get_follow_up_action_route(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    action = get_follow_up_action_by_id(
        db,
        action_id,
    )

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up action not found",
        )

    _require_action_access(
        current_user,
        action,
        db,
    )

    return action


# 4. Update follow-up action (doctor only)
@router.put("/{action_id}", response_model=FollowUpActionOut)
def update_follow_up_action_route(
    action_id: int,
    action_in: FollowUpActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update follow-up actions",
        )

    action = get_follow_up_action_by_id(
        db,
        action_id,
    )

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up action not found",
        )

    _require_action_access(
        current_user,
        action,
        db,
    )

    updated = update_follow_up_action(
        db,
        action_id,
        action_in,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up action not found",
        )

    return updated


# 5. Complete follow-up action (doctor only)
@router.post(
    "/{action_id}/complete",
    response_model=FollowUpActionOut,
)
def complete_follow_up_action_route(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "doctor":# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can complete follow-up actions",
        )

    action = get_follow_up_action_by_id(
        db,
        action_id,
    )

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up action not found",
        )

    _require_action_access(
        current_user,
        action,
        db,
    )

    completed = complete_follow_up_action(
        db,
        action_id,
    )

    if not completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action could not be completed",
        )

    return completed
