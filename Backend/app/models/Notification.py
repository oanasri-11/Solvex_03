"""Notification model."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    # Enum-like values stored as String: "alert", "reminder", "info"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    type = Column(String(50), nullable=False)  # alert | reminder | info
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):  # pragma: no cover
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type})>"
