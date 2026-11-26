"""SQLAlchemy engine, connection pool, and session management."""

import logging
from typing import Any, Dict, Generator, Optional
from urllib.parse import parse_qs, urlparse
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import normalize_database_url, settings

logger = logging.getLogger(__name__)

# Global engine cache (store raw target URL separately since str(engine.url) masks passwords)
_engine: Optional[Engine] = None
_engine_url: Optional[str] = None
_SessionFactory: Optional[sessionmaker[Session]] = None

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def _build_postgres_connect_args(target_url: str) -> Dict[str, Any]:
    """Build PostgreSQL connect_args supporting local Postgres and Supabase/PgBouncer poolers."""
    parsed = urlparse(target_url)
    query_params = parse_qs(parsed.query)
    is_local = bool(parsed.hostname and parsed.hostname.lower() in _LOCAL_HOSTS)
    connect_args: Dict[str, Any] = {
        "connect_timeout": min(settings.db_connect_timeout, 2) if is_local else settings.db_connect_timeout,
    }

    # Disable psycopg 3 server-side prepared statements for PgBouncer/Supavisor transaction pooler compatibility
    if "psycopg" in (parsed.scheme or ""):
        connect_args["prepare_threshold"] = None

    # Enforce SSL on non-local hosts (e.g. Supabase) unless explicitly configured in the URL
    if "sslmode" not in query_params:
        if settings.db_sslmode:
            connect_args["sslmode"] = settings.db_sslmode
        elif parsed.hostname and not is_local:
            connect_args["sslmode"] = "require"

    return connect_args


def get_engine(db_url: Optional[str] = None) -> Engine:
    """Return an active SQLAlchemy Engine instance (cached).

    Args:
        db_url: Optional database connection URL. If omitted, uses settings.database_url.

    Returns:
        Engine: Configured SQLAlchemy engine with pre-ping connection validation.
    """
    global _engine, _engine_url
    target_url = normalize_database_url(db_url or settings.database_url)

    if _engine is None or _engine_url != target_url:
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
                    "pool_size": settings.db_pool_size,
                    "max_overflow": settings.db_max_overflow,
                    "pool_timeout": 10,
                    "pool_recycle": 1800,
                    "connect_args": _build_postgres_connect_args(target_url),
                }
            )

        _engine = create_engine(target_url, **engine_kwargs)
        _engine_url = target_url

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
    db_name = eng.url.database or "postgres"
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "connected": True,
            "status": "connected",
            "dialect": eng.dialect.name,
            "database": db_name,
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
            "database": db_name,
            "error": sanitized_msg,
        }
    except Exception as exc:
        logger.warning("Unexpected error checking database connection: %s", exc)
        return {
            "connected": False,
            "status": "disconnected",
            "dialect": getattr(eng.dialect, "name", "unknown"),
            "database": db_name,
            "error": "Database service is unreachable",
        }
