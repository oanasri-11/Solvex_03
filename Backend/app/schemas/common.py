"""Common and shared Pydantic schemas."""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class IdResponse(BaseModel):
    """Generic ID response."""
    id: int


class ErrorResponse(BaseModel):
    """Generic error response."""
    detail: str
    code: Optional[str] = None


class PaginationParams(BaseModel):
    """Standard pagination query parameters."""
    skip: int = Field(0, ge=0, description="Records to skip")
    limit: int = Field(100, ge=1, le=500, description="Max records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated container."""
    items: List[T]
    total: int
    skip: int = 0
    limit: int = 100

