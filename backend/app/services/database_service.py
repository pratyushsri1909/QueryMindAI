"""Safe read-only SQL validation and execution service for QueryMind AI (Day 3).

SECURITY GUARANTEES:
--------------------
1. AST Inspection: Validates SQL statements using SQLGlot AST parsing before execution.
2. Read-Only Policy: Permits strictly SELECT and WITH...SELECT queries.
3. Modification Prohibition: Rejects INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, etc.
4. Single-Statement Enforcement: Rejects multiple concatenated SQL statements (prevents SQL injection chains).
5. Catalog Protection: Prohibits access to PostgreSQL system authentication and security catalogs (e.g. pg_shadow, pg_authid).
6. Credential Masking: Sanitizes all database exception messages to prevent connection URL or credential leakage.
"""

import logging
import re
import time
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

# System tables and catalogs prohibited from user queries
RESTRICTED_SYSTEM_TABLES = {
    "pg_shadow",
    "pg_authid",
    "pg_roles",
    "pg_database",
    "pg_user",
    "pg_auth_members",
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

    # Step 2: Enforce single-statement rule
    if not parsed_expressions:
        return False, "No valid SQL expressions detected in query."

    if len(parsed_expressions) > 1:
        return False, "Security violation: Multiple SQL statements are strictly prohibited."

    expr = parsed_expressions[0]

    # Step 3: Enforce top-level read-only query type (SELECT / UNION)
    if not isinstance(expr, (exp.Select, exp.Union)):
        expr_name = expr.key.upper() if hasattr(expr, "key") else "UNKNOWN"
        return False, f"Security violation: Only read-only SELECT queries are permitted (received {expr_name})."

    # Step 4: Scan entire AST tree for nested mutating expressions
    for node in expr.find_all(FORBIDDEN_AST_NODES):
        node_name = node.key.upper() if hasattr(node, "key") else "MUTATION"
        return False, f"Security violation: Modifying SQL operation '{node_name}' is strictly prohibited."

    # Step 5: Check for TRUNCATE keyword in expressions
    if "truncate" in sql.lower():
        return False, "Security violation: TRUNCATE statements are strictly prohibited."

    # Step 6: Verify table access against restricted system catalogs
    for table in expr.find_all(exp.Table):
        t_name = table.name.lower()
        if t_name in RESTRICTED_SYSTEM_TABLES:
            return False, f"Security violation: Access to system catalog table '{t_name}' is prohibited."

    return True, None


def _sanitize_db_error(error_str: str) -> str:
    """Strip connection credentials and passwords from database error messages."""
    sanitized = error_str.splitlines()[0] if error_str else "Database execution error."
    # Redact connection URIs
    sanitized = re.sub(r"://[^@]+@", "://***:***@", sanitized)
    return sanitized


def execute_read_query(
    sql: str,
    session: Optional[Session] = None,
    engine: Optional[Engine] = None,
    timeout_ms: Optional[int] = None,
) -> Dict[str, Any]:
    """Safely validate and execute a read-only SQL query against the database.

    Args:
        sql: Synthesized SQL query string.
        session: Optional SQLAlchemy Session. If provided, query runs within this session.
        engine: Optional custom SQLAlchemy Engine.
        timeout_ms: Statement timeout in milliseconds (defaults to settings.db_statement_timeout_ms).

    Returns:
        Dict[str, Any]: Structured execution payload compatible with frontend contract:
            - status: "database_success" or "error"
            - columns: List[str]
            - rows: List[List[Any]]
            - row_count: int
            - execution_time_ms: int
            - error: Optional[str]
    """
    # 1. Security & AST Validation
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

    try:
        # Determine execution context (Session vs Engine)
        if session is not None:
            # Session-based execution
            result = session.execute(text(sql))
            columns: List[str] = list(result.keys()) if result.returns_rows else []
            rows: List[List[Any]] = [list(row) for row in result.fetchall()] if result.returns_rows else []
        else:
            # Direct engine connection execution
            eng = engine or get_engine()
            with eng.connect() as conn:
                # Set PostgreSQL statement timeout if dialect is PostgreSQL
                if eng.dialect.name == "postgresql" and timeout_duration > 0:
                    try:
                        conn.execute(text(f"SET LOCAL statement_timeout = '{int(timeout_duration)}'"))
                    except Exception as t_err:
                        logger.debug("Could not set local statement_timeout: %s", t_err)

                result = conn.execute(text(sql))
                columns = list(result.keys()) if result.returns_rows else []
                rows = [list(row) for row in result.fetchall()] if result.returns_rows else []

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
        logger.exception("Unexpected error executing query: %s", exc)
        return {
            "status": "error",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": duration_ms,
            "error": f"Unexpected execution error: {str(exc)}",
        }

