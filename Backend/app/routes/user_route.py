"""User management API routes (Section 1)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_admin,
    get_current_user_any,
)
from app.models.user import User
from app.services.user_service import (
    get_user_by_id,
    get_all_users,
    create_user,
    update_user,
    update_preferences,
    deactivate_user,
)
from app.services.auth_service import change_password
from app.schemas.user import (
    UserOut,
    UserCreate,
    UserUpdate,
    UserPreferencesUpdate,
    UserListItem,
)
from app.schemas.auth import PasswordChangeRequest
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=UserOut)
def update_own_preferences(
    prefs: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Preferences: locale, timezone, text_size, theme, high_contrast, phone (resets phone_verified)."""
    updated = update_preferences(db, current_user.id, prefs)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated


@router.post("/me/change-password", response_model=MessageResponse)
def change_own_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Change own password."""
    success = change_password(db, current_user, data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    return MessageResponse(message="Password successfully changed")


@router.get("", response_model=List[UserListItem])
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List users (filters: role, is_active) - Administrator only."""
    return get_all_users(db, skip=skip, limit=limit, role=role, is_active=is_active)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_route(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create a user - Administrator only."""
    try:
        return create_user(db, user_in)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{id}", response_model=UserOut)
def read_user(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Read a user by ID - Administrator only."""
    user = get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{id}", response_model=UserOut)
def update_user_route(
    id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Change role or is_active - Administrator only."""
    user = update_user(db, id, user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{id}", response_model=MessageResponse)
def deactivate_user_route(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Deactivate (soft); revokes tokens, keeps all data - Administrator only."""
    user = deactivate_user(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return MessageResponse(message=f"User {id} deactivated successfully")
