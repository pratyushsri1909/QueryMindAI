"""Database schema initialization module for QueryMind AI."""

import logging
from typing import Optional
from sqlalchemy.engine import Engine

from app.database.models import Base
from app.database.session import get_engine

logger = logging.getLogger(__name__)


def init_database(engine: Optional[Engine] = None) -> None:
    """Create all provisional tables in the configured database if they do not exist.

    Args:
        engine: Optional custom SQLAlchemy Engine instance.
    """
    target_engine = engine or get_engine()
    logger.info("Initializing database tables for engine: %s", target_engine.url)
    Base.metadata.create_all(bind=target_engine)
    logger.info("Database schema initialization complete.")


def drop_database(engine: Optional[Engine] = None) -> None:
    """Drop all provisional tables in the configured database (useful for testing).

    Args:
        engine: Optional custom SQLAlchemy Engine instance.
    """
    target_engine = engine or get_engine()
    logger.warning("Dropping all database tables for engine: %s", target_engine.url)
    Base.metadata.drop_all(bind=target_engine)


if __name__ == "__main__":
    import sys

    eng = get_engine()
    if "--drop" in sys.argv:
        print(f"Dropping all tables on {eng.url.render_as_string(hide_password=True)}...")
        drop_database(eng)
    print(f"Creating tables on {eng.url.render_as_string(hide_password=True)}...")
    init_database(eng)
    print("Database tables initialized successfully.")

