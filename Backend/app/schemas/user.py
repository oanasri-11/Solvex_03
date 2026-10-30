"""Pydantic schemas for the User entity."""

from datetime import datetime
<<<<<<< HEAD
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    full_name: str
    role: str
    is_active: bool = True
    is_verified: bool = False
=======
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool = True
    email_verified: bool = False
    phone_verified: bool = False
    locale: Optional[str] = None
    timezone: Optional[str] = None
    text_size: int = Field(100, description="Text size: 100, 125, 150")
    theme: str = Field("light", description="Theme: light, calm_dark")
    high_contrast: bool = False
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
<<<<<<< HEAD
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
=======
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    text_size: Optional[int] = None
    theme: Optional[str] = None
    high_contrast: Optional[bool] = None
    password: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """Preferences update for the current user (PATCH /users/me)."""
    locale: Optional[str] = None
    timezone: Optional[str] = None
    text_size: Optional[int] = Field(None, description="Text size: 100, 125, 150")
    theme: Optional[str] = Field(None, description="Theme: light, calm_dark")
    high_contrast: Optional[bool] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    email_verified: bool
    phone_verified: bool
    locale: Optional[str] = None
    timezone: Optional[str] = None
    text_size: int
    theme: str
    high_contrast: bool
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
<<<<<<< HEAD
=======


class UserMeResponse(BaseModel):
    """Current user response for GET /auth/me."""
    id: int
    email: str
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    email_verified: bool
    phone_verified: bool
    locale: Optional[str] = None
    timezone: Optional[str] = None
    text_size: int
    theme: str
    high_contrast: bool
    created_at: datetime
    linked_patients: List[int] = []

    model_config = ConfigDict(from_attributes=True)


class UserListItem(BaseModel):
    """User list item for GET /users."""
    id: int
    email: str
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
