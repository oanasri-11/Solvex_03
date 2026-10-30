"""Pydantic schemas for the PatientProfile entity."""

from datetime import date, datetime
<<<<<<< HEAD
from typing import Optional

from pydantic import BaseModel, ConfigDict
=======
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class PatientProfileBase(BaseModel):
    user_id: int
<<<<<<< HEAD
=======
    first_name: Optional[str] = None
    last_name: Optional[str] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
<<<<<<< HEAD
=======
    age_band: Optional[str] = None  # 18-39, 40-64, 65-79, 80+
    under_treatment: Optional[bool] = False
    clinical_context: Optional[Dict[str, Any]] = None  # e.g. {"pregnancy_postpartum": true}
    target_systolic: Optional[int] = 135
    target_diastolic: Optional[int] = 85
    target_basis: Optional[str] = "home_average"
    target_set_by: Optional[int] = None
    target_set_at: Optional[datetime] = None
    rules_applicability: Optional[str] = "default_rules"
    enrolment_status: Optional[str] = "draft"  # draft, complete
    is_active: bool = True
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class PatientProfileCreate(PatientProfileBase):
    pass


<<<<<<< HEAD
class PatientProfileUpdate(BaseModel):
=======
class PatientEnrolRequest(BaseModel):
    """Enrol a patient (creates user and profile)."""
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    age_band: Optional[str] = None
    under_treatment: Optional[bool] = False
    clinical_context: Optional[Dict[str, Any]] = None


class PatientProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
<<<<<<< HEAD
=======
    age_band: Optional[str] = None
    under_treatment: Optional[bool] = None
    clinical_context: Optional[Dict[str, Any]] = None
    target_systolic: Optional[int] = None
    target_diastolic: Optional[int] = None
    is_active: Optional[bool] = None


class PatientSelfUpdate(BaseModel):
    """Patient editing own contact details (no clinical fields allowed)."""
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class PatientTargetUpdate(BaseModel):
    """Doctor setting individual home-BP target (SC4)."""
    systolic: int = Field(..., ge=90, le=200)
    diastolic: int = Field(..., ge=50, le=130)
    reason_code: Optional[str] = None
    note: Optional[str] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489


class PatientProfileOut(BaseModel):
    id: int
    user_id: int
<<<<<<< HEAD
=======
    first_name: Optional[str] = None
    last_name: Optional[str] = None
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
<<<<<<< HEAD
=======
    age_band: Optional[str] = None
    under_treatment: Optional[bool] = None
    clinical_context: Optional[Dict[str, Any]] = None
    target_systolic: Optional[int] = None
    target_diastolic: Optional[int] = None
    target_basis: Optional[str] = None
    target_set_by: Optional[int] = None
    target_set_at: Optional[datetime] = None
    rules_applicability: Optional[str] = None
    enrolment_status: Optional[str] = None
    is_active: bool
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
