"""Reports & Exports API routes (Section 20)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import (
    get_current_active_user,
    get_current_doctor,
    check_patient_access,
)
from app.models.user import User
from app.services.report_service import (
    preview_patient_report,
    start_report_export,
    get_export_job_status,
)
from app.schemas.report import (
    ReportPreviewOut,
    ReportExportRequest,
    ReportExportOut,
)

router = APIRouter(tags=["reports"])


@router.get("/doctor/patients/{id}/reports/preview", response_model=ReportPreviewOut)
def preview_report_route(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Preview structured clinical PDF/print report."""
    check_patient_access(current_user, id, db)
    try:
        return preview_patient_report(db, id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/doctor/patients/{id}/reports/export", response_model=ReportExportOut)
def export_report_route(
    id: int,
    export_in: ReportExportRequest = ReportExportRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Asynchronously generate formal report file (PDF/CSV)."""
    check_patient_access(current_user, id, db)
    return start_report_export(db, id, format=export_in.format)


@router.get("/doctor/reports/{job_id}")
def poll_export_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor),
):
    """Poll export job status and fetch download stream."""
    job = get_export_job_status(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return job
