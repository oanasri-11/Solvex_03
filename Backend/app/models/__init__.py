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
from app.models.DoctorProfile import DoctorProfile  # noqa: F401
from app.models.FollowUpAction import FollowUpAction  # noqa: F401
from app.models.MeasurementSchedule import MeasurementSchedule  # noqa: F401
from app.models.Notification import Notification  # noqa: F401
from app.models.PatientCondition import PatientCondition  # noqa: F401
from app.models.PatientHelpRequest import PatientHelpRequest  # noqa: F401
from app.models.PatientMonitoringMode import PatientMonitoringMode  # noqa: F401
from app.models.PatientProfile import PatientProfile  # noqa: F401
from app.models.PriorityAssessment import PriorityAssessment  # noqa: F401
from app.models.RuleVersion import RuleVersion  # noqa: F401
from app.models.ScheduleSlot import ScheduleSlot  # noqa: F401
from app.models.User import User  # noqa: F401

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
]
