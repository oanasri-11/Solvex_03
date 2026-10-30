
from fastapi import FastAPI
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
# Core API routes
from Backend.app.routes import (
    auth_route,
    user_route,
    patient_route,
    assignment_route,
    condition_route,
    schedule_route,
)

# Patient interaction routes
from Backend.app.routes import (
    reading_route,
    alertreading_route,
    help_requests,
    contact_request_route,
    notifications,
)

# Doctor workflow routes
from Backend.app.routes import (
    follow_up_action_route,
    audit_log_route,
    monotoring_mode_route,
    priority_route,
    rule_version_route,
    slot_route,
    ai,
)


# --------------------------------------------------
# Application
# --------------------------------------------------

app = FastAPI(
    title="Hypertension Follow-up API",
    description="API for hypertension patient monitoring and doctor follow-up.",
    version="1.0.0",
)


# --------------------------------------------------
# API Router Registration
# --------------------------------------------------

API_PREFIX = "/api/v1"

app.include_router(auth_route.router, prefix=API_PREFIX)
app.include_router(user_route.router, prefix=API_PREFIX)

app.include_router(patient_route.router, prefix=API_PREFIX)
app.include_router(assignment_route.router, prefix=API_PREFIX)
app.include_router(condition_route.router, prefix=API_PREFIX)
app.include_router(schedule_route.router, prefix=API_PREFIX)

app.include_router(reading_route.router, prefix=API_PREFIX)
app.include_router(alertreading_route.router, prefix=API_PREFIX)
app.include_router(help_requests.router, prefix=API_PREFIX)
app.include_router(contact_request_route.router, prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)

app.include_router(follow_up_action_route.router, prefix=API_PREFIX)
app.include_router(audit_log_route.router, prefix=API_PREFIX)
app.include_router(ai.router, prefix=API_PREFIX)


# --------------------------------------------------
# Basic Routes
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Hypertension Follow-up API is running",
        "version": "1.0.0",
    }


app.include_router(monotoring_mode_route.router, prefix=API_PREFIX)
app.include_router(priority_route.router, prefix=API_PREFIX)
app.include_router(rule_version_route.router, prefix=API_PREFIX)
app.include_router(slot_route.router, prefix=API_PREFIX)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }

