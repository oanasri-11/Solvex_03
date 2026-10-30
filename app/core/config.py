"""Application configuration.

Settings are sourced from environment variables (see ``.env``) with sensible
development defaults. Every value that is marked "TBD" in the API design doc is
kept here as a clearly marked placeholder with the note
"clinician validation required".
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    APP_NAME: str = "Solvex Hypertension Monitoring"
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./app.db"

    # -------------------------------------------------------------------------
    # JWT auth (access + refresh tokens)
    # -------------------------------------------------------------------------
    SECRET_KEY: str = "dev-secret-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -------------------------------------------------------------------------
    # Security / account lockout
    # -------------------------------------------------------------------------
    BCRYPT_ROUNDS: int = 12
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 30

    # -------------------------------------------------------------------------
    # Feature flags (open decisions, section 0 rule 10)
    # -------------------------------------------------------------------------
    FEATURE_CAREGIVER: bool = True
    FEATURE_LOW_BANDWIDTH_SMS: bool = False
    FEATURE_CONTEXT_FIELDS: bool = True
    FEATURE_ADMIN_ROLE: bool = True
    FEATURE_STREAKS: bool = False
    FEATURE_AI: bool = False

    # -------------------------------------------------------------------------
    # Versioned clinical rule config (placeholder - clinician validation required)
    # -------------------------------------------------------------------------
    DEFAULT_RULE_VERSION: str = "1.0.0"
    # Placeholder clinical thresholds. These MUST be validated by a clinician
    # before any real deployment. Values live in RuleVersion.config and are
    # never hard-coded in routes/services outside the rule engine.
    PLACEHOLDER_RULE_CONFIG: dict = {
        "status_levels": 5,
        "priority_levels": 4,
        "priority_not_triaged": "not_triaged",
        # Blood pressure thresholds (mmHg) - clinician validation required
        "reject_systolic_min": 40,
        "reject_systolic_max": 300,
        "reject_diastolic_min": 20,
        "reject_diastolic_max": 200,
        "unusual_systolic": 180,
        "unusual_diastolic": 120,
        "high_systolic": 140,
        "high_diastolic": 90,
        # Status level mapping (placeholder)
        "status_levels_config": {
            1: "optimal",
            2: "normal",
            3: "elevated",
            4: "high",
            5: "hypertensive_crisis",
        },
        # Escalation / missed slot timing - clinician validation required
        "missed_slot_minutes_after_due": 60,
        "escalation_minutes_after_missed": 120,
    }

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()