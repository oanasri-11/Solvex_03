"""User model."""


<<<<<<< HEAD
from sqlalchemy import Boolean, DateTime, Integer, String, func,Column
=======
from sqlalchemy import Boolean, DateTime, Integer, String, func, Column
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # Enum-like values stored as String: "patient", "doctor", "admin"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
<<<<<<< HEAD
=======
    phone = Column(String(50), unique=True, nullable=True, index=True)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # patient | doctor | admin
    is_active = Column(Boolean, default=True, nullable=False)
<<<<<<< HEAD
    is_verified = Column(Boolean, default=False, nullable=False)
=======
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    locale = Column(String(10), nullable=True)
    timezone = Column(String(64), nullable=True)
    text_size = Column(Integer, default=100, nullable=False)  # 100, 125, 150
    theme = Column(String(20), default="light", nullable=False)  # light, calm_dark
    high_contrast = Column(Boolean, default=False, nullable=False)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
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
<<<<<<< HEAD
    priority_assessments = relationship("PriorityAssessment", back_populates="assessor")
=======
    priority_assessments = relationship("PriorityAssessment", foreign_keys="[PriorityAssessment.assessor_id]")
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    case_reviews = relationship("CaseReview", back_populates="reviewer")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):  # pragma: no cover
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
