"""Pydantic schemas for the Notification entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    user_id: int
    type: str
    title: str
    message: Optional[str] = None
    is_read: bool


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: Optional[str] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
