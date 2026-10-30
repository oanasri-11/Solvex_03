"""Assignment service.

CRUD operations for the DoctorPatientAssignment model, following classic SQLAlchemy syntax.
Assignments are history records: there is no hard delete, only ending (deactivation).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.DoctorProfile import DoctorProfile
from app.models.PatientProfile import PatientProfile
from app.schemas.assignment import (
    DoctorPatientAssignmentCreate,
    DoctorPatientAssignmentUpdate,
    DoctorPatientAssignmentOut,
)


def create_assignment(
    db: Session, assignment_in: DoctorPatientAssignmentCreate
) -> Optional[DoctorPatientAssignment]:
    """Link a patient to a doctor. Verifies both records exist."""
    try:
        doctor = (
            db.query(DoctorProfile).filter(DoctorProfile.id == assignment_in.doctor_id).first()
        )
        patient = (
            db.query(PatientProfile).filter(PatientProfile.id == assignment_in.patient_id).first()
        )
        if not doctor or not patient:
            return None

        assigned_at = getattr(assignment_in, "assigned_at", None) or datetime.utcnow()
        is_active = getattr(assignment_in, "is_active", True)
        if is_active is None:
            is_active = True

        existing = (
            db.query(DoctorPatientAssignment)
            .filter(
                DoctorPatientAssignment.doctor_id == assignment_in.doctor_id,
                DoctorPatientAssignment.patient_id == assignment_in.patient_id,
            )
            .first()
        )
        if existing:
            existing.is_active = is_active
            existing.assigned_at = assigned_at
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        db_assignment = DoctorPatientAssignment(
            doctor_id=assignment_in.doctor_id,
            patient_id=assignment_in.patient_id,
            assigned_at=assigned_at,
            is_active=is_active,
        )
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except SQLAlchemyError:
        db.rollback()
        raise


def get_assignment_by_id(db: Session, assignment_id: int) -> Optional[DoctorPatientAssignment]:
    """Retrieve an assignment by its primary key."""
    return (
        db.query(DoctorPatientAssignment)
        .filter(DoctorPatientAssignment.id == assignment_id)
        .first()
    )


def get_all_assignments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    active: Optional[bool] = None,
):
    """List assignments with optional doctor_id / patient_id / active filters."""
    query = db.query(DoctorPatientAssignment)
    if doctor_id is not None:
        query = query.filter(DoctorPatientAssignment.doctor_id == doctor_id)
    if patient_id is not None:
        query = query.filter(DoctorPatientAssignment.patient_id == patient_id)
    if active is not None:
        query = query.filter(DoctorPatientAssignment.is_active == active)
    return query.offset(skip).limit(limit).all()


def update_assignment(
    db: Session, assignment_id: int, assignment_in: DoctorPatientAssignmentUpdate
) -> Optional[DoctorPatientAssignment]:
    """Update an existing assignment."""
    try:
        db_assignment = get_assignment_by_id(db, assignment_id)
        if not db_assignment:
            return None
        update_data = assignment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_assignment, field, value)
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except SQLAlchemyError:
        db.rollback()
        raise


def end_assignment(db: Session, assignment_id: int) -> Optional[DoctorPatientAssignment]:
    """End an assignment (set is_active = False). Assignments are history, never hard-deleted."""
    try:
        db_assignment = get_assignment_by_id(db, assignment_id)
        if not db_assignment:
            return None
        db_assignment.is_active = False
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except SQLAlchemyError:
        db.rollback()
        raise


def is_doctor_assigned(db: Session, doctor_id: int, patient_id: int) -> bool:
    """Check if an active assignment exists between doctor and patient."""
    assignment = (
        db.query(DoctorPatientAssignment)
        .filter(
            DoctorPatientAssignment.doctor_id == doctor_id,
            DoctorPatientAssignment.patient_id == patient_id,
            DoctorPatientAssignment.is_active == True,  # noqa: E712
        )
        .first()
    )
    return assignment is not None


def assert_doctor_has_access(db: Session, doctor_id: int, patient_id: int) -> bool:
    """Assert active assignment exists; returns True or False."""
    return is_doctor_assigned(db, doctor_id, patient_id)
