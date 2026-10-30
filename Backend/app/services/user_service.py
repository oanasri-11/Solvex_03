

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user record."""
    try:
        is_active = getattr(user_in, "is_active", True)
        if is_active is None:
            is_active = True
        email_verified = getattr(user_in, "email_verified", False)
        if email_verified is None:
            email_verified = False
        phone_verified = getattr(user_in, "phone_verified", False)
        if phone_verified is None:
            phone_verified = False
        locale = getattr(user_in, "locale", None)
        timezone = getattr(user_in, "timezone", None)
        text_size = getattr(user_in, "text_size", 100)
        theme = getattr(user_in, "theme", "light")
        high_contrast = getattr(user_in, "high_contrast", False)
        hashed_password = getattr(user_in, "hashed_password", None) or getattr(user_in, "password", "")

        db_user = User(
            email=user_in.email,
            phone=getattr(user_in, "phone", None),
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=is_active,
            email_verified=email_verified,
            phone_verified=phone_verified,
            locale=locale,
            timezone=timezone,
            text_size=text_size,
            theme=theme,
            high_contrast=high_contrast,
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


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """Retrieve a user by phone number."""
    return db.query(User).filter(User.phone == phone).first()


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


def update_preferences(
    db: Session,
    user_id: int,
    prefs_in,
) -> Optional[User]:
    """Update user preferences (locale, timezone, text_size, theme, high_contrast, phone)."""
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return None
        update_data = prefs_in.model_dump(exclude_unset=True)
        # Resetting phone also resets phone_verified
        if "phone" in update_data:
            db_user.phone = update_data.pop("phone")
            db_user.phone_verified = False
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
