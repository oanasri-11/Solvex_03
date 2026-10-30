"""Pydantic schemas for authentication and tokens."""

from typing import Optional
from pydantic import BaseModel, EmailStr


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

