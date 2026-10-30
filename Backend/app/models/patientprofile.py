"""PatientProfile model."""

<<<<<<< HEAD
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func,Column,Integer

=======
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func, Column, Integer, JSON
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import relationship

from app.db.base import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )
<<<<<<< HEAD
=======
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    date_of_birth = Column(Date, nullable=True)
    # Enum-like values stored as String: "male", "female", "other", "prefer_not_to_say"
    gender = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
<<<<<<< HEAD
=======

    # v3 fields
    age_band = Column(String(20), nullable=True)  # 18-39, 40-64, 65-79, 80+
    under_treatment = Column(Boolean, default=False, nullable=True)
    clinical_context = Column(JSON, nullable=True)  # flag pregnancy_postpartum etc.
    target_systolic = Column(Integer, default=135, nullable=True)
    target_diastolic = Column(Integer, default=85, nullable=True)
    target_basis = Column(String(50), default="home_average", nullable=True)
    target_set_by = Column(Integer, nullable=True)
    target_set_at = Column(DateTime(timezone=True), nullable=True)
    rules_applicability = Column(String(50), default="default_rules", nullable=True)
    enrolment_status = Column(String(50), default="draft", nullable=True)  # draft, complete
    is_active = Column(Boolean, default=True, nullable=False)

>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", uselist=False, back_populates="patient_profile")

    monitoring_mode = relationship(
        "PatientMonitoringMode", uselist=False, back_populates="patient", cascade="all, delete-orphan"
    )
    conditions = relationship("PatientCondition", back_populates="patient", cascade="all, delete-orphan")
    schedules = relationship("MeasurementSchedule", back_populates="patient", cascade="all, delete-orphan")
    readings = relationship("BloodPressureReading", back_populates="patient")
    alerts = relationship("Alert", back_populates="patient")
    priority_assessments = relationship("PriorityAssessment", back_populates="patient")
    case_reviews = relationship("CaseReview", back_populates="patient")
    help_requests = relationship("PatientHelpRequest", back_populates="patient")
    contact_requests = relationship("ContactRequest", back_populates="patient")
    follow_up_actions = relationship("FollowUpAction", back_populates="patient")
    assignments = relationship(
        "DoctorPatientAssignment", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self):  # pragma: no cover
        return f"<PatientProfile(id={self.id}, user_id={self.user_id})>"
