"""AI / LLM provider configuration.

This module extends the project's existing configuration layer
(``app.core.config``), which already loads the project ``.env`` file.  The
``AI_*`` variables below are additive: a deployer adds them to ``.env`` and they
never overwrite existing secrets or settings.
"""

import os
from typing import Optional

# ``app.core.config`` is imported here only to be sure the existing
# ``.env``-loading side effect has run; it is not duplicated.
from app.core import config as _core_config  # noqa: F401  # pragma: no cover

# New AI-specific environment variables (defaults are only used for local
# development until a real provider is configured).
AI_PROVIDER = os.getenv("AI_PROVIDER", "google_genai").strip().lower()
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash").strip()
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "30"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))

SUPPORTED_PROVIDERS = {"google_genai", "openai"}


def provider_is_configured(provider: Optional[str] = None) -> bool:
    """Return True when the selected provider has a usable API key."""
    p = (provider or AI_PROVIDER).strip().lower()
    if p not in SUPPORTED_PROVIDERS:
        return False
    return bool(AI_API_KEY)
