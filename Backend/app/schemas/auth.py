"""Pydantic schemas for authentication and tokens."""

<<<<<<< HEAD
from typing import Optional
from pydantic import BaseModel, EmailStr
=======
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    old_password: str
    new_password: str

<<<<<<< HEAD
=======

# --- Registration ---

class RegisterRequest(BaseModel):
    """Account registration request (enrolment code or caregiver invite code)."""
    email: EmailStr
    password: str
    full_name: str
    phone: str
    role: str = Field(..., description="patient | doctor | admin")
    enrolment_code: Optional[str] = Field(None, description="Enrolment code for public registration")
    caregiver_invite_code: Optional[str] = Field(None, description="Caregiver invite code")


class RegisterResponse(BaseModel):
    """Account registration response."""
    id: int
    email: str
    role: str
    is_active: bool
    email_verified: bool
    message: str


# --- Logout ---

class LogoutRequest(BaseModel):
    """Logout request - revoke the refresh token."""
    refresh_token: str


class LogoutResponse(BaseModel):
    """Logout response."""
    message: str


# --- Forgot / Reset password ---

class ForgotPasswordRequest(BaseModel):
    """Password reset request - send a reset link."""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Password reset response."""
    message: str


class ResetPasswordRequest(BaseModel):
    """Password reset with token."""
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    """Password reset response."""
    message: str


# --- Verify email ---

class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str


class VerifyEmailResponse(BaseModel):
    """Email verification response."""
    message: str


# --- Resend verification ---

class ResendVerificationRequest(BaseModel):
    """Resend verification email request."""
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """Resend verification response."""
    message: str


# --- Verify phone ---

class VerifyPhoneRequest(BaseModel):
    """Phone verification by one-time code."""
    phone: str
    code: str


class VerifyPhoneResponse(BaseModel):
    """Phone verification response."""
    message: str


# --- Resend phone code ---

class ResendPhoneCodeRequest(BaseModel):
    """Resend phone one-time code."""
    phone: str


class ResendPhoneCodeResponse(BaseModel):
    """Resend phone code response."""
    message: str

>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
