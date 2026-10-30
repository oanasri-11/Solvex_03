"""RuleVersion model."""

from sqlalchemy import Boolean, DateTime, Integer, String, func,Column
from sqlalchemy.dialects.postgresql import JSON

from app.db.base import Base


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    version = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_definition = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):  # pragma: no cover
        return f"<RuleVersion(id={self.id}, version={self.version}, rule_name={self.rule_name})>"
