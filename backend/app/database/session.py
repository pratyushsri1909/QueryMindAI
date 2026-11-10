"""SQLAlchemy engine, connection pool, and session management."""

import logging
from typing import Any, Dict, Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global engine cache
_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker[Session]] = None


def get_engine(db_url: Optional[str] = None) -> Engine:
    """Return an active SQLAlchemy Engine instance (cached).

    Args:
        db_url: Optional database connection URL. If omitted, uses settings.database_url.

    Returns:
        Engine: Configured SQLAlchemy engine with pre-ping connection validation.
    """
    global _engine
    target_url = db_url or settings.database_url

    if _engine is None or str(_engine.url) != target_url:
        # PostgreSQL specific pool configuration
        is_sqlite = target_url.startswith("sqlite")
        engine_kwargs: Dict[str, Any] = {
            "echo": False,
            "future": True,
        }

        if not is_sqlite:
            engine_kwargs.update(
                {
                    "pool_pre_ping": True,
                    "pool_size": 5,
                    "max_overflow": 10,
                    "pool_timeout": 5,
                    "pool_recycle": 1800,
                    "connect_args": {"connect_timeout": 2},
                }
            )

        _engine = create_engine(target_url, **engine_kwargs)

    return _engine


def get_session_factory(engine: Optional[Engine] = None) -> sessionmaker[Session]:
    """Return a configured SQLAlchemy SessionLocal factory."""
    global _SessionFactory
    eng = engine or get_engine()
    if _SessionFactory is None or _SessionFactory.kw.get("bind") != eng:
        _SessionFactory = sessionmaker(
            bind=eng,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a managed database session.

    Guarantees session termination and connection return to pool upon request completion.
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_db_connection(engine: Optional[Engine] = None) -> Dict[str, Any]:
    """Verify database reachability by executing a lightweight ping query (SELECT 1).

    Args:
        engine: Optional custom Engine instance. If omitted, uses standard application engine.

    Returns:
        Dict[str, Any]: Structured connection status dictionary without exposing credentials.
    """
    eng = engine or get_engine()
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "connected": True,
            "status": "connected",
            "dialect": eng.dialect.name,
            "error": None,
        }
    except SQLAlchemyError as err:
        # Sanitize error message to prevent database password leakage
        raw_msg = str(err).splitlines()[0] if str(err) else "Connection failed"
        # Mask any password in url if accidentally present in error
        sanitized_msg = raw_msg
        if "@" in sanitized_msg and "://" in sanitized_msg:
            sanitized_msg = "Database authentication or network connection failed."

        logger.warning("Database connection check failed: %s", sanitized_msg)
        return {
            "connected": False,
            "status": "disconnected",
            "dialect": eng.dialect.name,
            "error": sanitized_msg,
        }
    except Exception as exc:
        logger.warning("Unexpected error checking database connection: %s", exc)
        return {
            "connected": False,
            "status": "disconnected",
            "dialect": getattr(eng.dialect, "name", "unknown"),
            "error": "Database service is unreachable",
        }
