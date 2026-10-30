"""DoctorProfile model."""

from sqlalchemy import DateTime, ForeignKey, String, func,Column,Integer
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
    license_number = Column(String(100), unique=True, nullable=False, index=True)
    specialization = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", uselist=False, back_populates="doctor_profile")

    assignments = relationship(
        "DoctorPatientAssignment", back_populates="doctor", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover
        return f"<DoctorProfile(id={self.id}, license_number={self.license_number})>"
