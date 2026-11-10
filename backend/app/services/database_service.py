"""Safe read-only SQL validation and execution service for QueryMind AI (Day 4 Hardened).

SECURITY GUARANTEES:
--------------------
1. AST Inspection: Validates SQL statements using SQLGlot AST parsing before execution.
2. Read-Only Policy: Permits strictly SELECT and WITH...SELECT queries.
3. Modification Prohibition: Rejects INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, etc. via AST node inspection.
4. SELECT INTO Prohibition: Rejects top-level and nested SELECT ... INTO statements (prevents physical table creation).
5. Single-Statement Enforcement: Rejects multiple concatenated SQL statements (prevents SQL injection chains).
6. Catalog & Schema Protection: Prohibits access to PostgreSQL system catalogs (pg_settings, pg_tables, pg_class, pg_proc, pg_shadow, pg_authid) and system schemas (information_schema, pg_catalog).
7. Administrative Function Guard: Blocks dangerous PostgreSQL functions (pg_sleep, pg_terminate_backend, lo_export, pg_read_file).
8. Credential Masking: Sanitizes all database exception messages to prevent connection URL or credential leakage.
"""

import datetime
import logging
import re
import time
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
import sqlglot
from sqlglot import exp
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_engine

logger = logging.getLogger(__name__)

# System schemas prohibited from direct user queries
RESTRICTED_SYSTEM_SCHEMAS = {
    "information_schema",
    "pg_catalog",
    "pg_toast",
}

# System tables and catalogs prohibited from user queries
RESTRICTED_SYSTEM_TABLES = {
    # Authentication & User Catalogs
    "pg_shadow",
    "pg_authid",
    "pg_roles",
    "pg_database",
    "pg_user",
    "pg_auth_members",
    # System Configuration, Schema & Metadata Catalogs
    "pg_settings",
    "pg_tables",
    "pg_class",
    "pg_proc",
    "pg_stat_activity",
    "pg_stat_database",
    "pg_statistic",
    "pg_config",
    "pg_views",
    "pg_indexes",
}

# Dangerous PostgreSQL administrative, file I/O, and termination functions
RESTRICTED_FUNCTIONS = {
    # Denial of Service & Timing Delays
    "pg_sleep",
    "pg_sleep_for",
    "pg_sleep_until",
    # Server-Side File I/O & Large Object Export
    "pg_read_file",
    "pg_read_binary_file",
    "pg_write_file",
    "pg_write_binary_file",
    "lo_export",
    "lo_import",
    "lo_create",
    "lo_unlink",
    # Process & Session Termination / Administrative Control
    "pg_terminate_backend",
    "pg_cancel_backend",
    "pg_reload_conf",
    "pg_rotate_logfile",
}

# Forbidden SQL AST node types
FORBIDDEN_AST_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
    exp.TruncateTable,
    exp.Into,
)


def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    """Validate that a generated SQL string is a single, safe, read-only SELECT query.

    Args:
        sql: Generated SQL query string.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message_if_invalid)
    """
    if not sql or not sql.strip():
        return False, "SQL query cannot be empty or blank."

    # Step 1: Parse AST with SQLGlot (PostgreSQL dialect)
    try:
        parsed_expressions = [
            expr for expr in sqlglot.parse(sql, read="postgres") if expr is not None
        ]
    except Exception as parse_exc:
        logger.warning("SQL syntax parsing error: %s", parse_exc)
        return False, f"SQL syntax parsing failed: {str(parse_exc)}"

    # Filter out standalone semicolon tokens that SQLGlot parses for trailing comments or empty clauses
    statements = [
        expr for expr in parsed_expressions if not isinstance(expr, exp.Semicolon)
    ]

    # Step 2: Enforce single-statement rule
    if not statements:
        return False, "No valid SQL expressions detected in query."

    if len(statements) > 1:
        return False, "Security violation: Multiple SQL statements are strictly prohibited."

    expr = statements[0]

    # Step 3: Enforce top-level read-only query type (SELECT / UNION)
    if not isinstance(expr, (exp.Select, exp.Union)):
        expr_name = expr.key.upper() if hasattr(expr, "key") else "UNKNOWN"
        return False, f"Security violation: Only read-only SELECT queries are permitted (received {expr_name})."

    # Step 4: Reject SELECT ... INTO (both top-level and nested in CTEs or subqueries)
    if list(expr.find_all(exp.Into)):
        return False, "Security violation: SELECT ... INTO statements are strictly prohibited."

    # Step 5: Scan entire AST tree for nested mutating expressions
    for node in expr.find_all(FORBIDDEN_AST_NODES):
        node_name = node.key.upper() if hasattr(node, "key") else "MUTATION"
        return False, f"Security violation: Modifying SQL operation '{node_name}' is strictly prohibited."

    # Step 6: Verify table and schema access against restricted catalogs
    for table in expr.find_all(exp.Table):
        t_name = table.name.lower()
        t_schema = table.db.lower() if table.db else ""
        if t_schema in RESTRICTED_SYSTEM_SCHEMAS:
            return False, f"Security violation: Access to system schema '{t_schema}' is prohibited."
        if t_name in RESTRICTED_SYSTEM_TABLES:
            return False, f"Security violation: Access to system catalog table '{t_name}' is prohibited."

    # Step 7: Verify function calls against dangerous administrative functions
    for f in expr.find_all((exp.Anonymous, exp.Func)):
        func_name = ""
        if isinstance(f, exp.Anonymous):
            func_name = f.this.lower() if isinstance(f.this, str) else str(f.this).lower()
        elif hasattr(f, "sql_name") and callable(f.sql_name):
            func_name = f.sql_name().lower()
        elif hasattr(f, "name") and f.name:
            func_name = f.name.lower()
        else:
            func_name = f.key.lower()

        if func_name in RESTRICTED_FUNCTIONS:
            return False, f"Security violation: Execution of administrative function '{func_name}' is prohibited."

    return True, None


def _sanitize_db_error(error_str: str) -> str:
    """Strip connection credentials and passwords from database error messages."""
    sanitized = error_str.splitlines()[0] if error_str else "Database execution error."
    # Redact connection URIs
    sanitized = re.sub(r"://[^@]+@", "://***:***@", sanitized)
    return sanitized


def _serialize_value(val: Any) -> Any:
    """Recursively convert database return values to JSON-serializable primitives.

    Converts:
    - Decimal instances to int (if integral without fractional loss) or float.
    - datetime.date, datetime.datetime, and datetime.time to ISO 8601 strings.
    - uuid.UUID instances to standard strings.
    - Preserves str, int, float, bool, None.
    - Recursively processes nested lists, tuples, and dictionaries.
    """
    if isinstance(val, Decimal):
        return int(val) if val % 1 == 0 else float(val)
    if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
        return val.isoformat()
    if isinstance(val, uuid.UUID):
        return str(val)
    if isinstance(val, (list, tuple)):
        return [_serialize_value(item) for item in val]
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    return val


def execute_read_query(
    sql: str,
    session: Optional[Session] = None,
    engine: Optional[Engine] = None,
    timeout_ms: Optional[int] = None,
    *,
    params: Optional[Dict[str, Any]] = None,
    validate: bool = True,
) -> Dict[str, Any]:
    """Safely validate and execute a read-only SQL query against the database.

    Maintains complete backward compatibility with Day 3 positional parameters:
    (sql, session, engine, timeout_ms).

    Args:
        sql: Synthesized SQL query string.
        session: Optional SQLAlchemy Session. If provided, query runs within this session.
        engine: Optional custom SQLAlchemy Engine.
        timeout_ms: Statement timeout in milliseconds (defaults to settings.db_statement_timeout_ms).
        params: Optional dictionary of named query bind parameters (e.g. {"minimum_cgpa": 8.5}).
        validate: Internal testing-only hook. When False, bypasses SQLGlot AST validation to
            enable direct database engine timeout and error handling tests. Must NEVER be
            exposed to API routes or external user inputs (defaults to True).

    Returns:
        Dict[str, Any]: Structured execution payload compatible with frontend contract:
            - status: "database_success" or "error"
            - columns: List[str]
            - rows: List[List[Any]]
            - row_count: int
            - execution_time_ms: int
            - error: Optional[str]
    """
    # Defensive backward-compatibility: if a parameter dictionary is passed as 2nd positional argument
    if isinstance(session, dict) and params is None:
        params = session
        session = None

    # 1. Security & AST Validation (Testing hook: validate=False restricted to test harnesses)
    if validate:
        is_valid, validation_error = validate_sql(sql)
        if not is_valid:
            logger.warning("SQL validation rejected query: %s | Reason: %s", sql, validation_error)
            return {
                "status": "error",
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0,
                "error": validation_error,
            }

    start_time = time.perf_counter()
    timeout_duration = timeout_ms or settings.db_statement_timeout_ms
    query_params = params or {}

    try:
        # Determine execution context (Session vs Engine)
        if session is not None:
            # Session-based execution: enforce transaction-local statement timeout for PostgreSQL
            bind = session.get_bind() if hasattr(session, "get_bind") else None
            dialect_name = getattr(getattr(bind, "dialect", None), "name", "")
            if dialect_name == "postgresql" and timeout_duration > 0:
                try:
                    session.execute(
                        text("SELECT set_config('statement_timeout', :t_val, true)"),
                        {"t_val": str(int(timeout_duration))},
                    )
                except Exception as t_err:
                    logger.debug("Could not set session statement_timeout: %s", t_err)

            result = session.execute(text(sql), query_params)
            columns: List[str] = list(result.keys()) if result.returns_rows else []
            raw_rows = result.fetchall() if result.returns_rows else []
            rows: List[List[Any]] = [
                [_serialize_value(cell) for cell in row] for row in raw_rows
            ]
        else:
            # Direct engine connection execution: enforce connection statement timeout for PostgreSQL
            eng = engine or get_engine()
            with eng.connect() as conn:
                if eng.dialect.name == "postgresql" and timeout_duration > 0:
                    try:
                        conn.execute(
                            text("SELECT set_config('statement_timeout', :t_val, true)"),
                            {"t_val": str(int(timeout_duration))},
                        )
                    except Exception as t_err:
                        logger.debug("Could not set connection statement_timeout: %s", t_err)

                result = conn.execute(text(sql), query_params)
                columns = list(result.keys()) if result.returns_rows else []
                raw_rows = result.fetchall() if result.returns_rows else []
                rows = [
                    [_serialize_value(cell) for cell in row] for row in raw_rows
                ]

        duration_ms = max(1, round((time.perf_counter() - start_time) * 1000))

        return {
            "status": "database_success",
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "execution_time_ms": duration_ms,
            "error": None,
        }

    except SQLAlchemyError as sql_err:
        duration_ms = round((time.perf_counter() - start_time) * 1000)
        # Roll back session transaction if an error/timeout occurred to keep session clean
        if session is not None:
            try:
                session.rollback()
            except Exception as rb_err:
                logger.debug("Session rollback failed after query error: %s", rb_err)

        safe_msg = _sanitize_db_error(str(sql_err))
        logger.error("Database query execution error: %s", safe_msg)
        return {
            "status": "error",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": duration_ms,
            "error": f"Database execution error: {safe_msg}",
        }
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000)
        if session is not None:
            try:
                session.rollback()
            except Exception as rb_err:
                logger.debug("Session rollback failed after unexpected error: %s", rb_err)

        logger.exception("Unexpected error executing query: %s", exc)
        return {
            "status": "error",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": duration_ms,
            "error": f"Unexpected execution error: {str(exc)}",
        }

