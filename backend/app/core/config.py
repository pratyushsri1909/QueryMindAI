"""Application configuration settings for QueryMind AI backend."""

from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    """Core application settings and CORS configurations."""

    app_title: str = "QueryMind AI"
    app_description: str = "Natural Language to SQL Query Assistant"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
