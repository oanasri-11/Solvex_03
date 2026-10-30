<<<<<<< HEAD


from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
=======
"""DoctorPatientAssignment service (Section 4, UCLINK)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from sqlalchemy.orm import Session

from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.doctorprofile import DoctorProfile
from app.models.patientprofile import PatientProfile
<<<<<<< HEAD
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
            existing.is_active = is_active# type: ignore
            existing.assigned_at = assigned_at# type: ignore
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
=======
from app.models.Alert import Alert
from app.models.ContactRequest import ContactRequest
from app.models.CaseReview import CaseReview


def is_doctor_assigned(db: Session, doctor_id: int, patient_id: int) -> bool:
    """Check whether a doctor is actively assigned to a patient."""
    assignment = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).first()
    return assignment is not None


def assert_doctor_has_access(db: Session, doctor_id: int, patient_id: int) -> None:
    """Raise 404 if doctor is not assigned to patient (prevents leaking existence)."""
    if not is_doctor_assigned(db, doctor_id, patient_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )


def create_assignment(db: Session, assignment_in: Any) -> DoctorPatientAssignment:
    """Link a patient to a doctor."""
    doctor_id = assignment_in.doctor_id
    patient_id = assignment_in.patient_id

    doc = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")

    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")

    # Deactivate existing active assignment for this patient
    existing = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.patient_id == patient_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).all()
    for ex in existing:
        ex.is_active = False

    assignment = DoctorPatientAssignment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        is_active=True,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


def get_all_assignments(
    db: Session,
<<<<<<< HEAD
    skip: int = 0,
    limit: int = 100,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    active: Optional[bool] = None,
):
    """List assignments with optional doctor_id / patient_id / active filters."""
=======
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[DoctorPatientAssignment]:
    """Query assignments."""
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    query = db.query(DoctorPatientAssignment)
    if doctor_id is not None:
        query = query.filter(DoctorPatientAssignment.doctor_id == doctor_id)
    if patient_id is not None:
        query = query.filter(DoctorPatientAssignment.patient_id == patient_id)
    if active is not None:
        query = query.filter(DoctorPatientAssignment.is_active == active)
    return query.offset(skip).limit(limit).all()


<<<<<<< HEAD
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
        db_assignment.is_active = False# type: ignore
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except SQLAlchemyError:
        db.rollback()
        raise


def is_doctor_assigned(db: Session, doctor_id: int, patient_id: int) -> bool:# type: ignore
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
# type: ignore


def assert_doctor_has_access(db: Session, doctor_id: int, patient_id: int) -> bool: # type: ignore
    """Assert active assignment exists; returns True or False."""
    return is_doctor_assigned(db, doctor_id, patient_id)



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
=======
def get_doctor_patients(db: Session, doctor_id: int) -> List[Dict[str, Any]]:
    """Assigned patients, lightweight summary for doctor."""
    assignments = db.query(DoctorPatientAssignment).filter(
        DoctorPatientAssignment.doctor_id == doctor_id,
        DoctorPatientAssignment.is_active == True  # noqa: E712
    ).all()

    patients = []
    for a in assignments:
        p = db.query(PatientProfile).filter(PatientProfile.id == a.patient_id).first()
        if p:
            patients.append({
                "patient_id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "age_band": p.age_band,
                "target": {"systolic": p.target_systolic, "diastolic": p.target_diastolic},
                "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            })
    return patients


def end_assignment(
    db: Session,
    assignment_id: int,
    open_items: str = "transfer",
    new_doctor_id: Optional[int] = None,
    open_items_action: Optional[str] = None,
    transfer_doctor_id: Optional[int] = None,
) -> DoctorPatientAssignment:
    if open_items_action:
        open_items = open_items_action
    if transfer_doctor_id is not None:
        new_doctor_id = transfer_doctor_id
    """End an assignment; transfers open items to new doctor or raises 409 (Section 4)."""
    assignment = db.query(DoctorPatientAssignment).filter(DoctorPatientAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    if open_items == "transfer":
        if not new_doctor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Open alerts and reviews must be transferred to a new doctor; provide new_doctor_id."
            )
        # Create new assignment for transfer
        create_assignment(db, type("Obj", (), {"doctor_id": new_doctor_id, "patient_id": assignment.patient_id}))

    assignment.is_active = False
    db.commit()
    db.refresh(assignment)
    return assignment


def get_assignment_by_id(db: Session, assignment_id: int) -> Optional[DoctorPatientAssignment]:
    """Retrieve assignment by ID."""
    return db.query(DoctorPatientAssignment).filter(DoctorPatientAssignment.id == assignment_id).first()


def update_assignment(db: Session, assignment_id: int, update_in: Any) -> Optional[DoctorPatientAssignment]:
    """Update assignment fields."""
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        return None
    for field, val in update_in.dict(exclude_unset=True).items():
        setattr(assignment, field, val)
    db.commit()
    db.refresh(assignment)
    return assignment
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
