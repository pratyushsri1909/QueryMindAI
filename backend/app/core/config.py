"""Application configuration settings for QueryMind AI backend."""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env in backend/ or root directory if present
env_backend = Path(__file__).resolve().parent.parent.parent / ".env"
env_root = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if env_backend.exists():
    load_dotenv(dotenv_path=env_backend)
elif env_root.exists():
    load_dotenv(dotenv_path=env_root)
else:
    load_dotenv()


class Settings(BaseModel):
    """Core application settings, database configuration, and CORS policies."""

    app_title: str = "QueryMind AI"
    app_description: str = "Natural Language to SQL Query Assistant"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    # Execution Mode: "mock" (default Day 2 prototype) or "database" (PostgreSQL execution)
    querymind_mode: str = Field(
        default_factory=lambda: os.getenv("QUERYMIND_MODE", "mock").lower()
    )

    # PostgreSQL Database Connection URL (SQLAlchemy psycopg3 driver format)
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/querymind_db",
        )
    )

    # Database read query statement timeout (in milliseconds)
    db_statement_timeout_ms: int = Field(
        default_factory=lambda: int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "5000"))
    )

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
