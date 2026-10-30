
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import get_db
from app.models.user import User
from app.services.user_service import get_user_by_id

SECRET_KEY ="FwVoJL-7o0hDf5RI6RCeL6rbClFgEQlO82zVqbZuvQhYeJl_sYrvlkx3-NE29sKT"
ALGORITHM="HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account",
        )

    if not user.is_verified:# type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    return user

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.patient_service import get_patient_profile_by_user_id
from app.services.assignment_service import is_doctor_assigned


def check_patient_access(
    db: Session,
    current_user: User,
    patient_id: int,
):
    """
    Verify that the current user can access a patient.

    Patients: can access only their own profile.
    Doctors: can access only patients assigned to them.
    """

    if current_user.role == "patient":# type: ignore

        patient = get_patient_profile_by_user_id(
            db,
            current_user.id,# type: ignore
        )

        if not patient or patient.id != patient_id:# type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access this patient's data",
            )

        return patient

    elif current_user.role == "doctor":# type: ignore

        if not current_user.doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        assigned = is_doctor_assigned(
            db,
            current_user.doctor_profile.id,
            patient_id,
        )

        if not assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This patient is not assigned to you",
            )

        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )


