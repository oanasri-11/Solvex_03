from datetime import datetime, timedelta, timezone
from typing import Optional, cast

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.RevokedToken import RevokedToken
from app.schemas.auth import (
    LoginRequest,
    Token,
    TokenPayload,
    RefreshTokenRequest,
    PasswordChangeRequest,
    RegisterRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    VerifyPhoneRequest,
    ResendPhoneCodeRequest,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_jti,
    is_token_revoked,
    revoke_token,
)


# 1. Get user by email
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


# 2. Get user by ID
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


# 3. Get user by phone
def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    return db.query(User).filter(User.phone == phone).first()


# 4. Register user
def register_user(db: Session, user_data: RegisterRequest) -> User:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("Email already registered")

    if user_data.phone:
        existing_phone = get_user_by_phone(db, user_data.phone)
        if existing_phone:
            raise ValueError("Phone already registered")

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        email_verified=False,
        phone_verified=False,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


# 5. Authenticate user
def authenticate_user(
    db: Session,
    login_data: LoginRequest
) -> Optional[User]:

    user = get_user_by_email(db, login_data.email)

    if not user:
        return None

    if not verify_password(login_data.password, cast(str, user.hashed_password)):
        return None

    if not cast(bool, user.is_active):
        return None

    return user


# 6. Login and generate JWT tokens
def login_user(
    db: Session,
    login_data: LoginRequest
) -> Optional[Token]:

    user = authenticate_user(db, login_data)

    if not user:
        return None

    token_data = {
        "sub": str(user.id),
        "role": str(user.role),
        "email": str(user.email),
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# 7. Refresh access token
def refresh_access_token(
    db: Session,
    refresh_data: RefreshTokenRequest
) -> Optional[Token]:

    payload = decode_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        return None

    jti = payload.get("jti")
    if jti and is_token_revoked(db, jti):
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    user = get_user_by_id(db, int(user_id))

    if not user or not cast(bool, user.is_active):
        return None

    token_data = {
        "sub": str(user.id),
        "role": str(user.role),
        "email": str(user.email),
    }

    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
    )


# 8. Logout - revoke refresh token
def logout_user(
    db: Session,
    user: User,
    logout_data: LogoutRequest
) -> bool:
    """Revoke the refresh token."""
    payload = decode_token(logout_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        return False

    jti = payload.get("jti")
    if not jti:
        return False

    if is_token_revoked(db, jti):
        return True  # already revoked

    exp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc)

    revoke_token(db, jti, cast(int, user.id), "refresh", expires_at)
    return True


# 9. Change password
def change_password(
    db: Session,
    user: User,
    password_data: PasswordChangeRequest
) -> bool:

    if not verify_password(
        password_data.old_password,
        cast(str, user.hashed_password)
    ):
        return False

    setattr(user, "hashed_password", hash_password(password_data.new_password))

    try:
        db.commit()
        db.refresh(user)
        return True
    except Exception:
        db.rollback()
        raise


# 10. Forgot password - send reset link
def forgot_password(
    db: Session,
    forgot_data: ForgotPasswordRequest
) -> bool:
    """Send a password reset link (placeholder - email sending not implemented)."""
    user = get_user_by_email(db, forgot_data.email)
    if not user:
        return False  # Don't reveal whether email exists
    # In production, send email with reset token here
    return True


# 11. Reset password with token
def reset_password(
    db: Session,
    reset_data: ResetPasswordRequest
) -> bool:
    """Reset password using a reset token (placeholder - token validation not implemented)."""
    # In production, validate the reset token here
    return False


# 12. Verify email
def verify_email(
    db: Session,
    verify_data: VerifyEmailRequest
) -> bool:
    """Verify email using a verification token (placeholder - token validation not implemented)."""
    # In production, validate the verification token here
    return False


# 13. Resend verification email
def resend_verification(
    db: Session,
    resend_data: ResendVerificationRequest
) -> bool:
    """Resend the verification email (placeholder - email sending not implemented)."""
    user = get_user_by_email(db, resend_data.email)
    if not user:
        return False
    # In production, send verification email here
    return True


# 14. Verify phone
def verify_phone(
    db: Session,
    verify_data: VerifyPhoneRequest
) -> bool:
    """Verify phone by one-time code (placeholder - SMS sending not implemented)."""
    user = get_user_by_phone(db, verify_data.phone)
    if not user:
        return False
    # In production, validate the one-time code here
    setattr(user, "phone_verified", True)
    try:
        db.commit()
        db.refresh(user)
        return True
    except Exception:
        db.rollback()
        raise


# 15. Resend phone code
def resend_phone_code(
    db: Session,
    resend_data: ResendPhoneCodeRequest
) -> bool:
    """Resend the phone one-time code (placeholder - SMS sending not implemented)."""
    user = get_user_by_phone(db, resend_data.phone)
    if not user:
        return False
    # In production, send SMS with one-time code here
    return True
