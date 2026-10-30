"""User service.

CRUD operations for the User model, following classic SQLAlchemy syntax.
Password hash is never exposed through the service layer.
"""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.User import User
from app.schemas.user import UserCreate, UserUpdate, UserOut


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user record."""
    try:
        is_active = getattr(user_in, "is_active", True)
        if is_active is None:
            is_active = True
        is_verified = getattr(user_in, "is_verified", False)
        if is_verified is None:
            is_verified = False
        hashed_password = getattr(user_in, "hashed_password", None) or getattr(user_in, "password", "")

        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=is_active,
            is_verified=is_verified,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError:
        db.rollback()
        raise


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by its primary key."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by email (used by auth lookups)."""
    return db.query(User).filter(User.email == email).first()


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """List users with optional role / is_active filters."""
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """Update an existing user (role / is_active changes are admin-side)."""
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return None
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = update_data.pop("password")
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError:
        db.rollback()
        raise


def deactivate_user(db: Session, user_id: int) -> Optional[User]:
    """Soft deactivate a user (is_active = False). All data is kept."""
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return None
        db_user.is_active = False
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError:
        db.rollback()
        raise
