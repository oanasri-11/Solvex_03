"""Coverage and escalation targets service (Section 4b, RS-4, SC2c)."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.CoverageTarget import CoverageTarget
from app.models.doctorprofile import DoctorProfile


def get_coverage_for_doctor(db: Session, doctor_id: int) -> Optional[CoverageTarget]:
    """Retrieve coverage settings for doctor."""
    return db.query(CoverageTarget).filter(CoverageTarget.doctor_id == doctor_id).first()


def set_coverage_for_doctor(
    db: Session,
    doctor_id: int,
    backup_doctor_id: Optional[int] = None,
    after_hours_owner_id: Optional[int] = None,
    coverage_hours: Optional[Dict[str, Any]] = None,
) -> CoverageTarget:
    """Set backup doctor and after-hours owner (A, D)."""
    target = db.query(CoverageTarget).filter(CoverageTarget.doctor_id == doctor_id).first()
    if not target:
        target = CoverageTarget(
            doctor_id=doctor_id,
            backup_doctor_id=backup_doctor_id,
            after_hours_owner_id=after_hours_owner_id,
            coverage_hours=coverage_hours,
            version=1,
        )
        db.add(target)
    else:
        target.backup_doctor_id = backup_doctor_id
        target.after_hours_owner_id = after_hours_owner_id
        if coverage_hours:
            target.coverage_hours = coverage_hours
        target.version += 1
        target.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(target)
    return target


def get_all_coverage_entries(db: Session) -> List[CoverageTarget]:
    """Admin query of all coverage configurations."""
    return db.query(CoverageTarget).all()
