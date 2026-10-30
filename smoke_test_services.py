"""Smoke test: exercise every service function against a live SQLite DB."""
import sys
from datetime import datetime, date, timezone

from app.db.base import Base
from app.db.session import engine, SessionLocal

import app.models  # noqa: F401  register all models on Base

Base.metadata.create_all(bind=engine)

db = SessionLocal()
errors = []
count = 0


def try_call(label, fn):
    global count
    count += 1
    try:
        fn()
        print(f"  PASS {label}")
    except Exception as e:
        errors.append((label, type(e).__name__, str(e)))
        print(f"  FAIL {label} -> {type(e).__name__}: {e}")


from app.models.user import User
from app.models.patientprofile import PatientProfile
from app.models.doctorprofile import DoctorProfile
from app.models.Alert import Alert
from app.models.BloodPressureReading import BloodPressureReading
from app.models.AlertReading import AlertReading
from app.models.DoctorPatientAssignment import DoctorPatientAssignment
from app.models.CaseReview import CaseReview
from app.models.PatientCondition import PatientCondition
from app.models.ContactRequest import ContactRequest
from app.models.FollowUpAction import FollowUpAction
from app.models.PatientHelpRequest import PatientHelpRequest
from app.models.PatientMonitoringMode import PatientMonitoringMode
from app.models.Notification import Notification
from app.models.PriorityAssessment import PriorityAssessment
from app.models.MeasurementSchedule import MeasurementSchedule
from app.models.ScheduleSlot import ScheduleSlot
from app.models.Auditlog import AuditLog
from app.models.RuleVersion import RuleVersion

from app.schemas.user import UserCreate
from app.schemas.patient import PatientProfileCreate
from app.schemas.doctor import DoctorProfileCreate
from app.schemas.alert import AlertCreate, AlertUpdate
from app.schemas.measurement import BloodPressureReadingCreate
from app.schemas.alertreading import AlertReadingCreate
from app.schemas.assignment import DoctorPatientAssignmentCreate, DoctorPatientAssignmentUpdate
from app.schemas.audit_log import AuditLogCreate
from app.schemas.case_review import CaseReviewCreate, CaseReviewUpdate
from app.schemas.condition import PatientConditionCreate, PatientConditionUpdate
from app.schemas.contact_request import ContactRequestCreate, ContactRequestUpdate
from app.schemas.follow_up import FollowUpActionCreate, FollowUpActionUpdate
from app.schemas.help_request import PatientHelpRequestCreate
from app.schemas.monitoring_mode import PatientMonitoringModeCreate
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.schemas.priority import PriorityAssessmentCreate
from app.schemas.rule_version import RuleVersionCreate
from app.schemas.schedule import MeasurementScheduleCreate, MeasurementScheduleUpdate
from app.schemas.schedule_slot import ScheduleSlotCreate, ScheduleSlotUpdate

import app.services.user_service as us
import app.services.patient_service as ps
import app.services.doctor_service as ds
import app.services.alert_service as als
import app.services.reading_service as rs
import app.services.alert_reading_service as ars
import app.services.assignment_service as ass
import app.services.audit_log_service as alogs
import app.services.case_review_service as crs
import app.services.condition_service as cs
import app.services.contact_request_service as crqs
import app.services.follow_up_action_service as fus
import app.services.help_request_service as hrs
import app.services.monitoring_mode_service as mms
import app.services.notification_service as ns
import app.services.priority_service as prs
import app.services.rule_version_service as rvs
import app.services.schedule_service as ss
import app.services.slot_service as sls

# ---- seed users / profiles ----
try_call("create patient user", lambda: us.create_user(db, UserCreate(
    email="p@x.com", full_name="Pat User", role="patient", is_active=True, is_verified=True,
    hashed_password="x")))
try_call("create doctor user", lambda: us.create_user(db, UserCreate(
    email="d@x.com", full_name="Doc User", role="doctor", is_active=True, is_verified=True,
    hashed_password="x")))
try_call("create admin user", lambda: us.create_user(db, UserCreate(
    email="a@x.com", full_name="Admin User", role="admin", is_active=True, is_verified=True,
    hashed_password="x")))

db.commit()
patient_user = us.get_user_by_email(db, "p@x.com")
doctor_user = us.get_user_by_email(db, "d@x.com")

try_call("create patient profile", lambda: ps.create_patient_profile(db, PatientProfileCreate(
    user_id=patient_user.id, date_of_birth=date(1990, 1, 1), gender="female",
    phone="123", address="addr", emergency_contact_name="EC", emergency_contact_phone="456")))
try_call("create doctor profile", lambda: ds.create_doctor_profile(db, DoctorProfileCreate(
    user_id=doctor_user.id, license_number="LIC123", specialization="Cardiology", phone="789")))

db.commit()
patient = ps.get_patient_profile_by_user_id(db, patient_user.id)
doctor = ds.get_doctor_profile_by_user_id(db, doctor_user.id)


# ---- alert ----
try_call("create alert", lambda: als.create_alert(db, AlertCreate(
    patient_id=patient.id, alert_type="bp_high", severity="high", status="raised",
    message="High BP")))
db.commit()
alert = als.get_all_alerts(db)[0]

try_call("get alert by id", lambda: als.get_alert_by_id(db, alert.id))
try_call("update alert", lambda: als.update_alert(db, alert.id, AlertUpdate(status="delivered")))
try_call("acknowledge alert", lambda: als.acknowledge_alert(db, alert.id, doctor_user.id))
try_call("close alert", lambda: als.close_alert(db, alert.id, doctor_user.id))

# ---- reading ----
try_call("create reading", lambda: rs.create_blood_pressure_reading(db, BloodPressureReadingCreate(
    patient_id=patient.id, systolic=140, diastolic=90,
    measured_at=datetime.now(timezone.utc))))
db.commit()
reading = rs.get_all_blood_pressure_readings(db)[0]

try_call("get reading by id", lambda: rs.get_blood_pressure_reading_by_id(db, reading.id))

# ---- alert reading ----
try_call("create alert reading", lambda: ars.create_alert_reading(db, AlertReadingCreate(
    alert_id=alert.id, reading_id=reading.id)))
db.commit()

# ---- assignment ----
try_call("create assignment", lambda: ass.create_assignment(db, DoctorPatientAssignmentCreate(
    doctor_id=doctor.id, patient_id=patient.id,
    assigned_at=datetime.now(timezone.utc), is_active=True)))
db.commit()
assignment = ass.get_all_assignments(db)[0]

try_call("update assignment", lambda: ass.update_assignment(db, assignment.id, DoctorPatientAssignmentUpdate(is_active=False)))
try_call("end assignment", lambda: ass.end_assignment(db, assignment.id))

# ---- audit log ----
try_call("create audit log", lambda: alogs.create_audit_log_entry(db, AuditLogCreate(
    user_id=patient_user.id, action="create", table_name="users", record_id=patient_user.id)))
db.commit()

# ---- case review ----
try_call("create case review", lambda: crs.create_case_review(db, CaseReviewCreate(
    patient_id=patient.id, reviewer_id=doctor_user.id, status="draft",
    reviewed_at=datetime.now(timezone.utc), summary="summary")))
db.commit()
review = crs.get_all_case_reviews(db)[0]

try_call("update case review", lambda: crs.update_case_review(db, review.id, CaseReviewUpdate(status="completed")))

# ---- condition ----
try_call("create condition", lambda: cs.create_patient_condition(db, PatientConditionCreate(
    patient_id=patient.id, condition_name="Hypertension",
    diagnosed_at=date(2024, 1, 1), notes="notes", is_active=True)))
db.commit()
cond = cs.get_all_patient_conditions(db)[0]

try_call("update condition", lambda: cs.update_patient_condition(db, cond.id, PatientConditionUpdate(is_active=False)))
try_call("delete (soft) condition", lambda: cs.delete_patient_condition(db, cond.id))

# ---- contact request ----
try_call("create contact request", lambda: crqs.create_contact_request(db, ContactRequestCreate(
    patient_id=patient.id, doctor_id=doctor.id, message="hi", status="open")))
db.commit()
creq = crqs.get_all_contact_requests(db)[0]

try_call("update contact request", lambda: crqs.update_contact_request(db, creq.id, ContactRequestUpdate(status="in_progress")))
try_call("complete contact request", lambda: crqs.complete_contact_request(db, creq.id))

# ---- follow up action ----
try_call("create follow up action", lambda: fus.create_follow_up_action(db, FollowUpActionCreate(
    patient_id=patient.id, type="call", status="pending",
    due_date=datetime.now(timezone.utc), notes="call patient")))
db.commit()
fua = fus.get_all_follow_up_actions(db)[0]

try_call("update follow up action", lambda: fus.update_follow_up_action(db, fua.id, FollowUpActionUpdate(status="completed")))
try_call("delete follow up action", lambda: fus.delete_follow_up_action(db, fua.id))

# ---- help request ----
try_call("create help request", lambda: hrs.create_patient_help_request(db, PatientHelpRequestCreate(
    patient_id=patient.id, type="medication", status="open", description="need meds")))
db.commit()
hreq = hrs.get_all_patient_help_requests(db)[0]

try_call("cancel help request", lambda: hrs.cancel_patient_help_request(db, hreq.id))

# ---- monitoring mode ----
try_call("create monitoring mode", lambda: mms.create_monitoring_mode(db, PatientMonitoringModeCreate(
    patient_id=patient.id, mode="continuous")))
db.commit()
