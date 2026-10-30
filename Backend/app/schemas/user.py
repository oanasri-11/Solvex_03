"""Pydantic schemas for the User entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    full_name: str
    role: str
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
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
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
