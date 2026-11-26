"""Application configuration settings for QueryMind AI backend."""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables from .env in backend/ or root directory if present
env_backend = Path(__file__).resolve().parent.parent.parent / ".env"
env_root = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if env_backend.exists():
    load_dotenv(dotenv_path=env_backend)
elif env_root.exists():
    load_dotenv(dotenv_path=env_root)
else:
    load_dotenv()


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://querymind-ai.vercel.app",
]


def normalize_database_url(url: str) -> str:
    """Normalize PostgreSQL URLs (e.g. Supabase postgres:// or postgresql://) to psycopg 3."""
    if not isinstance(url, str):
        return url
    cleaned = url.strip()
    if cleaned.startswith("postgres://"):
        return "postgresql+psycopg://" + cleaned[len("postgres://") :]
    if cleaned.startswith("postgresql://"):
        return "postgresql+psycopg://" + cleaned[len("postgresql://") :]
    return cleaned


def load_cors_origins() -> List[str]:
    """Read comma-separated allowed origins from CORS_ORIGINS."""
    configured = os.getenv("CORS_ORIGINS")
    if configured is None or not configured.strip():
        return list(DEFAULT_CORS_ORIGINS)
    return [
        origin.strip().rstrip("/")
        for origin in configured.split(",")
        if origin.strip()
    ]


class Settings(BaseModel):
    """Core application settings, database configuration, and CORS policies."""

    app_title: str = "QueryMind AI"
    app_description: str = "Natural Language to SQL Query Assistant"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    # Execution Mode: "mock" (default prototype) or "database" (PostgreSQL execution)
    querymind_mode: str = Field(
        default_factory=lambda: os.getenv("QUERYMIND_MODE", "mock").strip().lower()
    )

    # PostgreSQL Database Connection URL (SQLAlchemy psycopg3 driver format)
    database_url: str = Field(
        default_factory=lambda: normalize_database_url(
            os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:postgres@localhost:5432/querymind_db",
            )
        )
    )

    # Database read query statement timeout (in milliseconds)
    db_statement_timeout_ms: int = Field(
        default_factory=lambda: int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "5000"))
    )

    # PostgreSQL connection establishment timeout (in seconds)
    db_connect_timeout: int = Field(
        default_factory=lambda: int(os.getenv("DB_CONNECT_TIMEOUT", "10"))
    )

    # Connection pool sizing (tuned for Supabase/Render free-tier limits)
    db_pool_size: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "5"))
    )
    db_max_overflow: int = Field(
        default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "5"))
    )

    # Optional explicit sslmode override (e.g. "require", "disable"); auto-required for remote hosts
    db_sslmode: str = Field(
        default_factory=lambda: os.getenv("DB_SSLMODE", "").strip()
    )

    cors_origins: List[str] = Field(default_factory=load_cors_origins)
    cors_origin_regex: Optional[str] = Field(
        default_factory=lambda: os.getenv("CORS_ORIGIN_REGEX") or None
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, value: str) -> str:
        return normalize_database_url(value)

    @field_validator("querymind_mode", mode="before")
    @classmethod
    def _normalize_mode(cls, value: str) -> str:
        return value.strip().lower() if isinstance(value, str) else value


settings = Settings()
