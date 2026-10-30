"""Backend FastAPI entry point."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import Base, engine
import app.models
from app.routes import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hypertension Monitoring System API",
    version="3.0.0",
    description="Hypertension Telemonitoring & Self-Monitoring Backend API (v3)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Hypertension Monitoring API v3 is running",
        "docs_url": "/docs",
        "api_v1_prefix": "/api/v1",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
