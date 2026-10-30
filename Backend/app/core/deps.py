"""Authentication and authorization dependencies for FastAPI routes."""

from typing import Optional
<<<<<<< HEAD
from fastapi import Depends, HTTPException, status
=======
from fastapi import Depends, HTTPException, Header, status
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_token
<<<<<<< HEAD
from app.models.User import User
=======
from app.models.user import User
from app.models.patientprofile import PatientProfile
from app.models.CaregiverLink import CaregiverLink
from app.models.Consent import Consent
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
from app.services.assignment_service import is_doctor_assigned

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate bearer token and retrieve the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    sub = payload.get("sub")
    if not sub:
        raise credentials_exception

    # Subject can be user ID (int or str) or email
    user = None
    try:
        user_id = int(sub)
        user = db.query(User).filter(User.id == user_id).first()
    except (ValueError, TypeError):
        user = db.query(User).filter(User.email == str(sub)).first()

    if not user:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return current_user


<<<<<<< HEAD
=======
def get_current_user_any(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the current user regardless of active status (for "Any" access endpoints)."""
    return current_user


>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user has the admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_current_doctor(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user is a doctor or admin."""
    if current_user.role not in ("doctor", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor privileges required",
        )
    return current_user


def get_current_patient(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user is a patient or admin."""
    if current_user.role not in ("patient", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient privileges required",
        )
    return current_user


<<<<<<< HEAD
=======
def get_current_caregiver_or_patient(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user is a patient, caregiver, or admin."""
    if current_user.role not in ("patient", "caregiver", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient or caregiver privileges required",
        )
    return current_user


>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
def check_patient_access(
    current_user: User,
    patient_id: int,
    db: Session,
) -> bool:
    """Verify that current_user has access to patient_id.
    
    - Admin: full access
    - Patient: can only access own patient profile
    - Doctor: can only access actively assigned patients (404 if not assigned)
<<<<<<< HEAD
=======
    - Caregiver: can only access linked patients with active consent
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    """
    if current_user.role == "admin":
        return True

    if current_user.role == "patient":
        if not current_user.patient_profile or current_user.patient_profile.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this patient's data",
            )
        return True

<<<<<<< HEAD
=======
    if current_user.role == "caregiver":
        link = db.query(CaregiverLink).filter(
            CaregiverLink.caregiver_user_id == current_user.id,
            CaregiverLink.patient_id == patient_id,
            CaregiverLink.status == "active"
        ).first()
        if not link:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized as caregiver for this patient",
            )
        # Check active consent
        consent = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.type == "caregiver_access",
            Consent.withdrawn_at.is_(None)
        ).first()
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active caregiver consent not found",
            )
        return True

>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
    if current_user.role == "doctor":
        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )
        doctor_id = current_user.doctor_profile.id
        if not is_doctor_assigned(db, doctor_id, patient_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found or not assigned to doctor",
            )
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )

<<<<<<< HEAD
=======

def resolve_acting_patient_id(
    current_user: User,
    db: Session,
    x_acting_for: Optional[int] = None,
    required_scope: Optional[str] = None,
) -> int:
    """Resolve acting patient ID for /patients/me/... calls.
    
    If current_user is a patient -> returns current_user.patient_profile.id.
    If current_user is a caregiver -> checks X-Acting-For, CaregiverLink, and caregiver_access consent.
    """
    if current_user.role == "patient":
        if not current_user.patient_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
        return current_user.patient_profile.id

    if current_user.role == "caregiver":
        if not x_acting_for:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Acting-For header is required for caregiver requests"
            )
        link = db.query(CaregiverLink).filter(
            CaregiverLink.caregiver_user_id == current_user.id,
            CaregiverLink.patient_id == x_acting_for,
            CaregiverLink.status == "active"
        ).first()
        if not link:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CAREGIVER_SCOPE: No active link for patient")
        
        if required_scope and required_scope not in (link.scope or []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"CAREGIVER_SCOPE: Scope '{required_scope}' not granted"
            )

        consent = db.query(Consent).filter(
            Consent.patient_id == x_acting_for,
            Consent.type == "caregiver_access",
            Consent.withdrawn_at.is_(None)
        ).first()
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CAREGIVER_SCOPE: Patient has not granted active caregiver_access consent"
            )
        return x_acting_for

    if current_user.role == "admin":
        if x_acting_for:
            return x_acting_for
        if current_user.patient_profile:
            return current_user.patient_profile.id
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin must specify acting patient ID")

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CAREGIVER_SCOPE: Unauthorized role")
>>>>>>> 4e52f68428b0d6100ad60954edfda790fa8a3489
