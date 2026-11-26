"""Main entry point for the QueryMind AI FastAPI backend application."""

from typing import Dict
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router as api_router
from app.database.session import check_db_connection

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
)

# Configure CORS for local development and deployed Vercel origin
cors_kwargs = {
    "allow_origins": settings.cors_origins,
    "allow_credentials": "*" not in settings.cors_origins,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.cors_origin_regex:
    cors_kwargs["allow_origin_regex"] = settings.cors_origin_regex

app.add_middleware(CORSMiddleware, **cors_kwargs)

# Mount modular API router under /api/v1
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root Welcome Endpoint",
    response_model=Dict[str, str],
)
def read_root() -> Dict[str, str]:
    """Root endpoint returning service identification and running status."""
    return {
        "message": "Welcome to QueryMind AI",
        "status": "Backend is running",
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check Endpoint",
    response_model=Dict[str, str],
)
def health_check(include_db: bool = False) -> Dict[str, str]:
    """Health check endpoint indicating whether the backend service is operational.

    Args:
        include_db: If True, tests live database connectivity and includes mode/database metadata.
    """
    payload: Dict[str, str] = {"status": "healthy"}
    if include_db:
        db_info = check_db_connection()
        payload["database"] = db_info["status"]
        payload["mode"] = settings.querymind_mode
        if db_info.get("database"):
            payload["database_name"] = db_info["database"]
    return payload
