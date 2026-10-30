"""DoctorProfile model."""

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, Column, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    specialization = Column(String(255), nullable=True)
    speciality = Column(String(100), nullable=True)
    facility = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notification_preferences = Column(JSON, nullable=True)  # in_app, email, sms per tier

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", uselist=False, back_populates="doctor_profile")
    assignments = relationship(
        "DoctorPatientAssignment", back_populates="doctor", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover
        return f"<DoctorProfile(id={self.id}, user_id={self.user_id}, license={self.license_number})>"
