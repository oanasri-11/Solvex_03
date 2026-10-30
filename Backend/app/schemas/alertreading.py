"""Pydantic schemas for the AlertReading entity."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertReadingBase(BaseModel):
    alert_id: int
    reading_id: int


class AlertReadingCreate(AlertReadingBase):
    pass


class AlertReadingUpdate(BaseModel):
    alert_id: Optional[int] = None
    reading_id: Optional[int] = None


class AlertReadingOut(BaseModel):
    id: int
    alert_id: int
    reading_id: int

    model_config = ConfigDict(from_attributes=True)