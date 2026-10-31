"""Core security module: password hashing and JWT token handling."""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pathlib import Path
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

try:
    from dotenv import load_dotenv
    load_dotenv()
    parent_env = Path(__file__).resolve().parent.parent.parent / ".env"
    if parent_env.exists():
        load_dotenv(parent_env)
    root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
except Exception:
    pass

# ==========================================
# Configuration
# ==========================================

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-ME-in-production")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not configured")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)


# ==========================================
# Password Hashing
# ==========================================

import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False


# ==========================================
# JWT Token Creation
# ==========================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a short-lived access token."""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    jti = str(uuid.uuid4())

    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": jti,
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(
    data: Dict[str, Any]
) -> str:
    """Create a long-lived refresh token."""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    jti = str(uuid.uuid4())

    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": jti,
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================================
# JWT Token Verification
# ==========================================

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token."""

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None


def get_token_jti(token: str) -> Optional[str]:
    """Extract the JTI claim from a token without verifying expiry."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": False},
        )
        return payload.get("jti")
    except JWTError:
        return None


def is_token_revoked(db, jti: str) -> bool:
    """Check whether a JTI has been revoked."""
    from app.models.RevokedToken import RevokedToken
    return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None


def revoke_token(db, jti: str, user_id: int, token_type: str, expires_at: datetime) -> None:
    """Revoke a token by storing its JTI."""
    from app.models.RevokedToken import RevokedToken
    db.add(RevokedToken(
        jti=jti,
        user_id=user_id,
        token_type=token_type,
        expires_at=expires_at,
    ))
    db.commit()
