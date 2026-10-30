"""Authentication API routes (Section 1)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_current_user_any,
)
from app.models.user import User
from app.models.CaregiverLink import CaregiverLink
from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user,
    change_password,
    forgot_password,
    reset_password,
    verify_email,
    resend_verification,
    verify_phone,
    resend_phone_code,
)
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    LogoutRequest,
    LogoutResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyPhoneRequest,
    VerifyPhoneResponse,
    ResendPhoneCodeRequest,
    ResendPhoneCodeResponse,
    PasswordChangeRequest,
    Token,
)
from app.schemas.user import UserMeResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Create an account with an enrolment code or a caregiver invite code."""
    try:
        user = register_user(db, user_data)
        return RegisterResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            email_verified=user.email_verified,
            message="Account registered successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """Email and password, returns access and refresh tokens."""
    token = login_user(db, login_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Generate a new access token from a valid refresh token."""
    token = refresh_access_token(db, refresh_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.post("/logout", response_model=LogoutResponse)
def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_any),
):
    """Revoke the refresh token."""
    success = logout_user(db, current_user, logout_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not revoke token",
        )
    return LogoutResponse(message="Successfully logged out")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password_route(
    forgot_data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Send a password reset link."""
    forgot_password(db, forgot_data)
    return ForgotPasswordResponse(message="If the email exists, a password reset link has been sent.")


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password_route(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Set a new password with the reset token."""
    success = reset_password(db, reset_data)
    if not success:
        return ResetPasswordResponse(message="Password reset request processed.")
    return ResetPasswordResponse(message="Password has been successfully reset.")


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email_route(
    verify_data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """Verify email address."""
    verify_email(db, verify_data)
    return VerifyEmailResponse(message="Email verification processed.")


@router.post("/resend-verification", response_model=ResendVerificationResponse)
def resend_verification_route(
    resend_data: ResendVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_any),
):
    """Resend the verification email."""
    resend_verification(db, resend_data)
    return ResendVerificationResponse(message="Verification email sent.")


@router.post("/verify-phone", response_model=VerifyPhoneResponse)
def verify_phone_route(
    verify_data: VerifyPhoneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_any),
):
    """Confirm phone by one-time code."""
    success = verify_phone(db, verify_data)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
    return VerifyPhoneResponse(message="Phone number successfully verified.")


@router.post("/resend-phone-code", response_model=ResendPhoneCodeResponse)
def resend_phone_code_route(
    resend_data: ResendPhoneCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_any),
):
    """Resend the one-time phone code."""
    resend_phone_code(db, resend_data)
    return ResendPhoneCodeResponse(message="Verification code sent to phone.")


@router.get("/me", response_model=UserMeResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user_any),
    db: Session = Depends(get_db),
):
    """Current user, role, profile summary, active mode; for caregiver, list of linked patients."""
    linked = []
    if current_user.role == "caregiver":
        links = db.query(CaregiverLink).filter(
            CaregiverLink.caregiver_user_id == current_user.id,
            CaregiverLink.status == "active",
        ).all()
        linked = [l.patient_id for l in links]

    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        phone_verified=current_user.phone_verified,
        locale=current_user.locale,
        timezone=current_user.timezone or "Africa/Algiers",
        text_size=current_user.text_size or 100,
        theme=current_user.theme or "light",
        high_contrast=current_user.high_contrast or False,
        created_at=current_user.created_at,
        linked_patients=linked,
    )


@router.post("/change-password", response_model=MessageResponse)
def change_password_route(
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
