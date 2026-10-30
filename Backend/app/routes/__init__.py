"""API routes package: configures and exposes the central /api/v1 router."""

from fastapi import APIRouter

from app.routes.auth_route import router as auth_router
from app.routes.user_route import router as user_router
from app.routes.patient_route import router as patient_router
from app.routes.doctor_route import router as doctor_router
from app.routes.assignment_route import router as assignment_router
from app.routes.coverage_route import router as coverage_router
from app.routes.monitoring_mode_route import router as monitoring_mode_router
from app.routes.caregiver_route import router as caregiver_router
from app.routes.consent_route import router as consent_router
from app.routes.condition_route import router as condition_router
from app.routes.treatment_event_route import router as treatment_event_router
from app.routes.office_reading_route import router as office_reading_router
from app.routes.schedule_route import router as schedule_router
from app.routes.slot_route import router as slot_router
from app.routes.reminder_route import router as reminder_router
from app.routes.reading_route import router as reading_router
from app.routes.device_route import router as device_router
from app.routes.alert_route import router as alert_router
from app.routes.priority_route import router as priority_router
from app.routes.config_route import router as config_router
from app.routes.review_route import router as review_router
from app.routes.help_request_route import router as help_request_router
from app.routes.contact_request_route import router as contact_request_router
from app.routes.notification_route import router as notification_router
from app.routes.report_route import router as report_router
from app.routes.rule_version_route import router as rule_version_router
from app.routes.audit_log_route import router as audit_log_router
from app.routes.ai_route import router as ai_router

# Central API v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(patient_router)
api_router.include_router(doctor_router)
api_router.include_router(assignment_router)
api_router.include_router(coverage_router)
api_router.include_router(monitoring_mode_router)
api_router.include_router(caregiver_router)
api_router.include_router(consent_router)
api_router.include_router(condition_router)
api_router.include_router(treatment_event_router)
api_router.include_router(office_reading_router)
api_router.include_router(schedule_router)
api_router.include_router(slot_router)
api_router.include_router(reminder_router)
api_router.include_router(reading_router)
api_router.include_router(device_router)
api_router.include_router(alert_router)
api_router.include_router(priority_router)
api_router.include_router(config_router)
api_router.include_router(review_router)
api_router.include_router(help_request_router)
api_router.include_router(contact_request_router)
api_router.include_router(notification_router)
api_router.include_router(report_router)
api_router.include_router(rule_version_router)
api_router.include_router(audit_log_router)
api_router.include_router(ai_router)

__all__ = ["api_router"]
