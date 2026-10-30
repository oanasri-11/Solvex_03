"""User model."""


from sqlalchemy import Boolean, DateTime, Integer, String, func,Column
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # Enum-like values stored as String: "patient", "doctor", "admin"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # patient | doctor | admin
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # One-to-one profiles
    patient_profile = relationship(
        "PatientProfile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    doctor_profile = relationship(
        "DoctorProfile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )

    # One-to-many
    priority_assessments = relationship("PriorityAssessment", back_populates="assessor")
    case_reviews = relationship("CaseReview", back_populates="reviewer")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):  # pragma: no cover
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
