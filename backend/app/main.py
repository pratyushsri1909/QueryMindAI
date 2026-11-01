"""Main entry point for the QueryMind AI FastAPI backend application."""

from typing import Dict
from fastapi import FastAPI, status

app = FastAPI(
    title="QueryMind AI",
    description="Natural Language to SQL Query Assistant",
    version="1.0.0",
)


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
def health_check() -> Dict[str, str]:
    """Health check endpoint indicating whether the backend service is operational."""
    return {
        "status": "healthy",
    }
