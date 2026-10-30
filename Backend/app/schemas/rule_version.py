"""Pydantic schemas for the RuleVersion entity."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class RuleVersionBase(BaseModel):
    version: str
    rule_name: str
    rule_definition: Optional[Any] = None
    is_active: bool


class RuleVersionCreate(RuleVersionBase):
    pass


class RuleVersionUpdate(BaseModel):
    version: Optional[str] = None
    rule_name: Optional[str] = None
    rule_definition: Optional[Any] = None
    is_active: Optional[bool] = None


class RuleVersionOut(BaseModel):
    id: int
    version: str
    rule_name: str
    rule_definition: Optional[Any] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
