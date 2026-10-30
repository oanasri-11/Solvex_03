
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

# Replace with the actual location of your authentication dependency.
from app.core.deps import get_current_active_user# type: ignore

from app.services.user_service import (
    get_user_by_id,
)

from app.schemas.user import (
    UserOut,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# 1. Get current authenticated user
@router.get(
    "/me",
    response_model=UserOut,
)
def get_current_user_route(
    current_user: User = Depends(get_current_active_user),
):
    """Get the profile of the currently authenticated user."""

    return current_user


# 2. Get user by ID
@router.get(
    "/{user_id}",
    response_model=UserOut,
)
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Users can only access their own account."""

    if current_user.id != user_id:# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own account",
        )

    user = get_user_by_id(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
