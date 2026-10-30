"""RevokedToken model for tracking revoked JWT refresh tokens."""

from sqlalchemy import Boolean, DateTime, Integer, String, func, Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    jti = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token_type = Column(String(20), nullable=False)  # "access" or "refresh"
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):  # pragma: no cover
        return f"<RevokedToken(id={self.id}, jti={self.jti}, user_id={self.user_id})>"
