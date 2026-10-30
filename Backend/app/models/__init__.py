"""Models package: imports every ORM model so that ``Base.metadata`` is fully
populated once this package is imported (required for ``create_all`` and
migration autogeneration).
"""

from app.models.Alert import Alert  # noqa: F401
from app.models.AlertReading import AlertReading  # noqa: F401
from app.models.Auditlog import AuditLog  # noqa: F401
from app.models.BloodPressureReading import BloodPressureReading  # noqa: F401
from app.models.CaseReview import CaseReview  # noqa: F401
from app.models.ContactRequest import ContactRequest  # noqa: F401
from app.models.DoctorPatientAssignment import DoctorPatientAssignment  # noqa: F401
from app.models.doctorprofile import DoctorProfile  # noqa: F401
from app.models.FollowUpAction import FollowUpAction  # noqa: F401
from app.models.MeasurementSchedule import MeasurementSchedule  # noqa: F401
from app.models.Notification import Notification  # noqa: F401
from app.models.PatientCondition import PatientCondition  # noqa: F401
from app.models.PatientHelpRequest import PatientHelpRequest  # noqa: F401
from app.models.PatientMonitoringMode import PatientMonitoringMode  # noqa: F401
from app.models.patientprofile import PatientProfile  # noqa: F401
from app.models.PriorityAssessment import PriorityAssessment  # noqa: F401
from app.models.RevokedToken import RevokedToken  # noqa: F401
from app.models.RuleVersion import RuleVersion  # noqa: F401
from app.models.ScheduleSlot import ScheduleSlot  # noqa: F401
from app.models.user import User  # noqa: F401

# v3 Models
from app.models.Consent import Consent  # noqa: F401
from app.models.CaregiverLink import CaregiverLink  # noqa: F401
from app.models.TreatmentEvent import TreatmentEvent  # noqa: F401
from app.models.OfficeReading import OfficeReading  # noqa: F401
from app.models.CoverageTarget import CoverageTarget  # noqa: F401
from app.models.ReminderPreference import ReminderPreference  # noqa: F401
from app.models.ConnectedDevice import ConnectedDevice  # noqa: F401
from app.models.ModeChangeRequest import ModeChangeRequest  # noqa: F401
from app.models.TargetRecord import TargetRecord  # noqa: F401

__all__ = [
    "Alert",
    "AlertReading",
    "AuditLog",
    "BloodPressureReading",
    "CaseReview",
    "ContactRequest",
    "DoctorPatientAssignment",
    "DoctorProfile",
    "FollowUpAction",
    "MeasurementSchedule",
    "Notification",
    "PatientCondition",
    "PatientHelpRequest",
    "PatientMonitoringMode",
    "PatientProfile",
    "PriorityAssessment",
    "RuleVersion",
    "ScheduleSlot",
    "User",
    "RevokedToken",
    "Consent",
    "CaregiverLink",
    "TreatmentEvent",
    "OfficeReading",
    "CoverageTarget",
    "ReminderPreference",
    "ConnectedDevice",
    "ModeChangeRequest",
    "TargetRecord",
]
