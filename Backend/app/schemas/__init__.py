"""Pydantic schemas package: re-exports every entity schema."""

from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    Token,
    TokenPayload,
    RegisterRequest,
    RegisterResponse,
    LogoutRequest,
    LogoutResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyPhoneRequest,
    VerifyPhoneResponse,
    ResendPhoneCodeRequest,
    ResendPhoneCodeResponse,
)
from app.schemas.common import (
    ErrorResponse,
    IdResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertOut,
    AlertUpdate,
    AlertAcknowledgeRequest,
    AlertPatientAcknowledgeRequest,
    AlertCloseRequest,
)
from app.schemas.alertreading import (
    AlertReadingBase,
    AlertReadingCreate,
    AlertReadingOut,
    AlertReadingUpdate,
)
from app.schemas.audit_log import (
    AuditLogBase,
    AuditLogCreate,
    AuditLogOut,
    AuditLogUpdate,
)
from app.schemas.assignment import (
    DoctorPatientAssignmentBase,
    DoctorPatientAssignmentCreate,
    DoctorPatientAssignmentOut,
    DoctorPatientAssignmentUpdate,
)
from app.schemas.case_review import (
    CaseReviewBase,
    CaseReviewCreate,
    CaseReviewOut,
    CaseReviewUpdate,
)
from app.schemas.contact_request import (
    ContactRequestBase,
    ContactRequestCreate,
    ContactRequestOut,
    ContactRequestUpdate,
)
from app.schemas.condition import (
    PatientConditionBase,
    PatientConditionCreate,
    PatientConditionOut,
    PatientConditionUpdate,
)
from app.schemas.doctor import (
    DoctorProfileBase,
    DoctorProfileCreate,
    DoctorProfileOut,
    DoctorProfileUpdate,
    DoctorNotificationPreferencesUpdate,
)
from app.schemas.follow_up import (
    FollowUpActionBase,
    FollowUpActionCreate,
    FollowUpActionOut,
    FollowUpActionUpdate,
)
from app.schemas.help_request import (
    PatientHelpRequestBase,
    PatientHelpRequestCreate,
    PatientHelpRequestOut,
    PatientHelpRequestUpdate,
)
from app.schemas.measurement import (
    BloodPressureReadingBase,
    BloodPressureReadingCreate,
    BloodPressureReadingOut,
    BloodPressureReadingUpdate,
    ReadingConfirmRequest,
    ReadingAnnotateRequest,
)
from app.schemas.monitoring_mode import (
    PatientMonitoringModeBase,
    PatientMonitoringModeCreate,
    PatientMonitoringModeOut,
    PatientMonitoringModeUpdate,
)
from app.schemas.notification import (
    NotificationBase,
    NotificationCreate,
    NotificationOut,
    NotificationUpdate,
)
from app.schemas.patient import (
    PatientProfileBase,
    PatientProfileCreate,
    PatientProfileOut,
    PatientProfileUpdate,
    PatientEnrolRequest,
    PatientSelfUpdate,
    PatientTargetUpdate,
)
from app.schemas.priority import (
    PriorityAssessmentBase,
    PriorityAssessmentCreate,
    PriorityAssessmentOut,
    PriorityAssessmentUpdate,
)
from app.schemas.rule_version import (
    RuleVersionBase,
    RuleVersionCreate,
    RuleVersionOut,
    RuleVersionUpdate,
)
from app.schemas.schedule import (
    MeasurementScheduleBase,
    MeasurementScheduleCreate,
    MeasurementScheduleOut,
    MeasurementScheduleUpdate,
)
from app.schemas.schedule_slot import (
    ScheduleSlotBase,
    ScheduleSlotCreate,
    ScheduleSlotOut,
    ScheduleSlotUpdate,
    SlotConfirmRequest,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserOut,
    UserUpdate,
    UserPreferencesUpdate,
    UserMeResponse,
    UserListItem,
)

# v3 Schemas
from app.schemas.caregiver import (
    CaregiverInvitationRequest,
    CaregiverInvitationResponse,
    CaregiverLinkOut,
)
from app.schemas.consent import (
    ConsentCreate,
    ConsentAdminCreate,
    ConsentOut,
    ConsentTextOut,
    ConsentStateOut,
)
from app.schemas.coverage import (
    CoverageTargetCreate,
    CoverageTargetUpdate,
    CoverageTargetOut,
)
from app.schemas.device import (
    ConnectedDeviceCreate,
    ConnectedDeviceOut,
    InboundSMSWebhook,
    DeviceBatchSyncRequest,
)
from app.schemas.office_reading import (
    OfficeReadingCreate,
    OfficeReadingOut,
)
from app.schemas.reminder import (
    ReminderPreferenceUpdate,
    ReminderPreferenceOut,
    PushTokenRequest,
    ReminderSlotOut,
)
from app.schemas.treatment_event import (
    TreatmentEventCreate,
    TreatmentEventCorrect,
    TreatmentEventOut,
    CurrentMedicationsOut,
)
from app.schemas.mode_change_request import (
    ModeChangeRequestCreate,
    ModeChangeResolveRequest,
    ModeChangeRequestOut,
)
from app.schemas.report import (
    ReportExportRequest,
    ReportExportOut,
    ReportPreviewOut,
)
from app.schemas.ai import (
    AISummaryResponse,
    AIAlertExplanationResponse,
)
from app.schemas.config import (
    PatientContentResponse,
    LabelsResponse,
    FeaturesResponse,
)
