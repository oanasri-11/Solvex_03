from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    Token,
    TokenPayload,
    RefreshTokenRequest,
    PasswordChangeRequest,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


# 1. Get user by email
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


# 2. Get user by ID
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


# 3. Register user
def register_user(db: Session, user_data) -> User:
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        is_verified=False,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


# 4. Authenticate user
def authenticate_user(
    db: Session,
    login_data: LoginRequest
) -> Optional[User]:

    user = get_user_by_email(db, login_data.email)

    if not user:
        return None

    if not verify_password(login_data.password, user.password_hash):
        return None

    if not user.is_active:
        return None

    if not user.is_verified:
        return None

    return user


# 5. Login and generate JWT tokens
def login_user(
    db: Session,
    login_data: LoginRequest
) -> Optional[Token]:

    user = authenticate_user(db, login_data)

    if not user:
        return None

    token_data = {
        "sub": str(user.id),
        "role": user.role,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# 6. Refresh access token
def refresh_access_token(
    db: Session,
    refresh_data: RefreshTokenRequest
) -> Optional[Token]:

    payload = decode_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    user = get_user_by_id(db, int(user_id))

    if not user or not user.is_active or not user.is_verified:
        return None

    token_data = {
        "sub": str(user.id),
        "role": user.role,
    }

    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
    )


# 7. Change password
def change_password(
    db: Session,
    user: User,
    password_data: PasswordChangeRequest
) -> bool:

    if not verify_password(
        password_data.old_password,
        user.password_hash
    ):
        return False

    user.password_hash = hash_password(password_data.new_password)

    try:
        db.commit()
        db.refresh(user)
        return True
    except Exception:
        db.rollback()
        raise