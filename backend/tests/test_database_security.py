"""Security regression tests for QueryMind AI SQL validation and safe execution.

Verifies that:
1. Dangerous functions (nextval, setval, advisory locks, pg_notify, pg_sleep, file access) are strictly rejected.
2. Modifying operations (INSERT, UPDATE, DELETE, MERGE, DDL, SELECT INTO) are strictly rejected.
3. Multiple statements and stacked injections are strictly rejected.
4. Nested queries, CTEs, and formatting bypass attempts are strictly rejected.
5. Legitimate read-only SELECT queries with aggregates, joins, filters, grouping, and bound parameters pass.
"""

import pytest
from app.services.database_service import validate_sql, execute_read_query


# ---------------------------------------------------------------------------
# 1. Dangerous Functions Rejection Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql,expected_keyword",
    [
        # Sequence modification and stateful functions
        ("SELECT nextval('student_id_seq');", "nextval"),
        ("SELECT setval('student_id_seq', 100);", "setval"),
        ("SELECT currval('student_id_seq');", "currval"),
        ("SELECT lastval();", "lastval"),
        # Advisory locks & locking side effects
        ("SELECT pg_advisory_lock(1234);", "pg_advisory_lock"),
        ("SELECT pg_advisory_lock_shared(1234);", "pg_advisory_lock_shared"),
        ("SELECT pg_advisory_unlock(1234);", "pg_advisory_unlock"),
        ("SELECT pg_advisory_unlock_all();", "pg_advisory_unlock_all"),
        ("SELECT pg_advisory_xact_lock(1234);", "pg_advisory_xact_lock"),
        ("SELECT pg_try_advisory_lock(1234);", "pg_try_advisory_lock"),
        # Inter-process messaging & notifications
        ("SELECT pg_notify('app_events', 'payload');", "pg_notify"),
        # Timing delays and denial of service
        ("SELECT pg_sleep(5);", "pg_sleep"),
        ("SELECT pg_sleep_for('5 seconds');", "pg_sleep_for"),
        ("SELECT pg_sleep_until('2030-01-01');", "pg_sleep_until"),
        # Server-side file I/O & system introspection
        ("SELECT pg_read_file('postgresql.conf');", "pg_read_file"),
        ("SELECT pg_read_binary_file('pg_hba.conf');", "pg_read_binary_file"),
        ("SELECT pg_write_file('evil.txt', 'data');", "pg_write_file"),
        ("SELECT pg_ls_dir('.');", "pg_ls_dir"),
        ("SELECT pg_stat_file('postgresql.conf');", "pg_stat_file"),
        ("SELECT lo_export(1, '/tmp/evil.txt');", "lo_export"),
        ("SELECT lo_import('/etc/passwd');", "lo_import"),
        ("SELECT lo_create(0);", "lo_create"),
        ("SELECT lo_unlink(1);", "lo_unlink"),
        # Process and session termination
        ("SELECT pg_terminate_backend(1234);", "pg_terminate_backend"),
        ("SELECT pg_cancel_backend(1234);", "pg_cancel_backend"),
        ("SELECT pg_reload_conf();", "pg_reload_conf"),
        ("SELECT pg_rotate_logfile();", "pg_rotate_logfile"),
        ("SELECT set_config('statement_timeout', '0', false);", "set_config"),
        # External query execution
        ("SELECT dblink_exec('evil', 'DROP TABLE students;');", "dblink_exec"),
        ("SELECT query_to_xml('SELECT * FROM students', true, false, '');", "query_to_xml"),
    ],
)
def test_dangerous_functions_rejected(sql: str, expected_keyword: str):
    """Verify that dangerous sequence, advisory lock, notification, sleep, and file functions are blocked."""
    is_valid, err = validate_sql(sql)
    assert is_valid is False, f"Expected {sql} to be rejected"
    assert "Security violation" in err
    assert expected_keyword in err.lower() or "unapproved function" in err.lower()


# ---------------------------------------------------------------------------
# 2. Mutating Statements Rejection Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql,expected_term",
    [
        ("INSERT INTO students (name, cgpa) VALUES ('Eve', 9.5);", "INSERT"),
        ("UPDATE students SET cgpa = 10.0 WHERE student_id = 1;", "UPDATE"),
        ("DELETE FROM students WHERE student_id = 1;", "DELETE"),
        ("DROP TABLE students;", "DROP"),
        ("ALTER TABLE students ADD COLUMN hacked TEXT;", "ALTER"),
        ("TRUNCATE TABLE students;", "TRUNCATE"),
        ("CREATE TABLE evil_table (id INT);", "CREATE"),
        ("MERGE INTO students USING courses ON students.department = courses.department WHEN MATCHED THEN UPDATE SET cgpa = 10.0;", "MERGE"),
        ("GRANT ALL ON students TO PUBLIC;", "GRANT"),
        ("REVOKE ALL ON students FROM PUBLIC;", "REVOKE"),
        ("COPY students TO '/tmp/students.csv';", "COPY"),
        ("LOCK TABLE students IN ACCESS EXCLUSIVE MODE;", "LOCK"),
        ("ANALYZE students;", "ANALYZE"),
    ],
)
def test_mutating_statements_rejected(sql: str, expected_term: str):
    """Verify that all DDL, DML, administration, and grant operations are blocked."""
    is_valid, err = validate_sql(sql)
    assert is_valid is False, f"Expected {sql} to be rejected"
    assert "Security violation" in err


# ---------------------------------------------------------------------------
# 3. SELECT INTO and Write-Capable SELECT Forms
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * INTO new_table FROM students;",
        "SELECT name, cgpa INTO copy_table FROM students WHERE cgpa > 8.5;",
        "SELECT student_id INTO TEMP temp_students FROM students;",
        "SELECT student_id INTO UNLOGGED unlogged_students FROM students;",
        "WITH cte AS (SELECT * INTO nested_into FROM students) SELECT * FROM cte;",
        "SELECT * FROM (SELECT * INTO subquery_into FROM students) s;",
        "SELECT * FROM students FOR UPDATE;",
        "SELECT * FROM students FOR SHARE;",
        "SELECT * FROM students FOR NO KEY UPDATE;",
        "SELECT * FROM students FOR KEY SHARE;",
    ],
)
def test_write_capable_select_forms_rejected(sql: str):
    """Verify that SELECT INTO and row-locking SELECT variants are strictly blocked."""
    is_valid, err = validate_sql(sql)
    assert is_valid is False, f"Expected {sql} to be rejected"
    assert "Security violation" in err


# ---------------------------------------------------------------------------
# 4. Multi-Statement and Stacked Injection Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM students; DROP TABLE students;",
        "SELECT * FROM students; DELETE FROM courses;",
        "SELECT * FROM students; SELECT pg_sleep(5);",
        "SELECT 1; SELECT 2;",
        "SELECT * FROM students; -- comment\nDROP TABLE courses;",
        "SELECT * FROM students; /* comment */ DELETE FROM enrollments;",
    ],
)
def test_multi_statement_queries_rejected(sql: str):
    """Verify that chained or stacked SQL statements are rejected unconditionally."""
    is_valid, err = validate_sql(sql)
    assert is_valid is False, f"Expected {sql} to be rejected"
    assert "Security violation" in err or "Multiple SQL statements" in err


# ---------------------------------------------------------------------------
# 5. Nested and CTE Bypass Attempts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        "WITH cte AS (DELETE FROM students RETURNING *) SELECT * FROM cte;",
        "WITH cte AS (INSERT INTO students (name) VALUES ('x') RETURNING *) SELECT * FROM cte;",
        "WITH cte AS (UPDATE students SET cgpa = 9.9 RETURNING *) SELECT * FROM cte;",
        "WITH cte AS (SELECT nextval('student_seq') AS n) SELECT * FROM cte;",
        "WITH cte AS (SELECT pg_advisory_lock(1) AS l) SELECT * FROM cte;",
        "SELECT * FROM students WHERE student_id = (SELECT nextval('student_seq'));",
        "SELECT * FROM students WHERE pg_notify('chan', 'msg') IS NOT NULL;",
        "SELECT * FROM students, (SELECT pg_advisory_lock(99)) AS l;",
        "SELECT * FROM students WHERE (SELECT pg_sleep(5)) IS NULL;",
        "SELECT * FROM students WHERE department IN (SELECT pg_read_file('conf'));",
        "SELECT pg_catalog.pg_sleep(1);",
        "SELECT pg_catalog.nextval('s');",
        "SELECT information_schema.tables.table_name FROM information_schema.tables;",
    ],
)
def test_nested_and_cte_bypasses_rejected(sql: str):
    """Verify that unsafe operations hidden in CTEs, subqueries, or schema qualifiers are caught."""
    is_valid, err = validate_sql(sql)
    assert is_valid is False, f"Expected {sql} to be rejected"
    assert "Security violation" in err


# ---------------------------------------------------------------------------
# 6. Unapproved Function Allowlist Enforcement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        "SELECT custom_hacker_function() FROM students;",
        "SELECT evil_proc(name) FROM students;",
        "SELECT sys_eval('whoami');",
        "SELECT user_defined_mutation(1);",
    ],
)
def test_unapproved_functions_rejected_by_allowlist(sql: str):
    """Verify that non-allowlisted functions are blocked by the safe function allowlist."""
    is_valid, err = validate_sql(sql)
    assert is_valid is False
    assert "Security violation" in err
    assert "unapproved function" in err.lower() or "administrative" in err.lower()


# ---------------------------------------------------------------------------
# 7. Positive Tests: Legitimate Read-Only Queries
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        # Simple projection and filtering
        "SELECT student_id, name, batch, cgpa, department FROM students;",
        "SELECT name, cgpa FROM students WHERE cgpa > 8.5;",
        "SELECT * FROM courses WHERE department = 'CSE';",
        # Multi-table JOIN
        (
            "SELECT s.name, c.course_name, e.grade "
            "FROM students s "
            "INNER JOIN enrollments e ON s.student_id = e.student_id "
            "INNER JOIN courses c ON e.course_id = c.course_id "
            "WHERE e.semester = 'Fall 2024';"
        ),
        # Aggregate functions, grouping, and ordering
        "SELECT department, COUNT(*) AS student_count FROM students GROUP BY department;",
        "SELECT department, AVG(cgpa) AS avg_cgpa FROM students GROUP BY department ORDER BY avg_cgpa DESC;",
        "SELECT MIN(cgpa) AS lowest, MAX(cgpa) AS highest, SUM(credits) AS total FROM students, courses;",
        "SELECT department, ROUND(AVG(cgpa), 2) AS rounded_avg FROM students GROUP BY department;",
        # String and conditional functions
        "SELECT UPPER(name), LOWER(department), COALESCE(batch, 2024) FROM students;",
        "SELECT student_id, CONCAT(name, ' (', department, ')') AS label FROM students;",
        "SELECT SUBSTRING(course_name, 1, 10), LENGTH(course_name) FROM courses;",
        # Limits and offsets
        "SELECT name, cgpa FROM students ORDER BY cgpa DESC LIMIT 5 OFFSET 0;",
        # Parameterized queries
        "SELECT name, cgpa FROM students WHERE cgpa > :p0 AND department = :p1;",
        "SELECT * FROM students WHERE department IN (:d0, :d1);",
        # Legitimate CTEs
        "WITH top_students AS (SELECT name, cgpa FROM students WHERE cgpa > 9.0) SELECT * FROM top_students;",
    ],
)
def test_legitimate_queries_pass_validation(sql: str):
    """Verify that legitimate SELECT queries, joins, aggregates, groupings, and bound params pass."""
    is_valid, err = validate_sql(sql)
    assert is_valid is True, f"Expected {sql} to pass validation, got error: {err}"
    assert err is None


# ---------------------------------------------------------------------------
# 8. Execution-Level Read-Only Rejection via execute_read_query
# ---------------------------------------------------------------------------

def test_execute_read_query_blocks_mutations_before_execution():
    """Verify that execute_read_query returns structured error for mutating queries."""
    res = execute_read_query("INSERT INTO students (name) VALUES ('Hacker');")
    assert res["status"] == "error"
    assert "Security violation" in res["error"]
    assert res["row_count"] == 0


# ---------------------------------------------------------------------------
# 9. Fail-Closed Read-Only Enforcement Tests
# ---------------------------------------------------------------------------

def test_execute_read_query_engine_fails_closed_when_readonly_cannot_be_set():
    """Verify that if set_config('transaction_read_only') fails on an Engine connection,
    the user query is aborted, the connection is rolled back, and user SQL is not executed.
    """
    from unittest.mock import MagicMock
    from sqlalchemy.exc import OperationalError

    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    mock_conn.execution_options.return_value = mock_conn

    # First call is set_config('transaction_read_only'...), which fails
    mock_conn.execute.side_effect = OperationalError("Simulated read-only failure", None, None)

    res = execute_read_query("SELECT name FROM students;", engine=mock_engine)

    assert res["status"] == "error"
    assert "Failed to enforce read-only transaction mode" in res["error"]
    assert res["row_count"] == 0
    # Crucial: verify connection rollback was called to close the transaction safely
    mock_conn.rollback.assert_called_once()
    # Verify user query was not executed after the failure (only 1 execute call for set_config)
    assert mock_conn.execute.call_count == 1


def test_execute_read_query_session_fails_closed_when_readonly_cannot_be_set():
    """Verify that if set_config('transaction_read_only') fails on a Session,
    the query is aborted, session rolled back, and user SQL is not executed.
    """
    from unittest.mock import MagicMock
    from sqlalchemy.exc import OperationalError

    mock_session = MagicMock()
    mock_bind = MagicMock()
    mock_bind.dialect.name = "postgresql"
    mock_session.get_bind.return_value = mock_bind

    # First call is set_config('transaction_read_only'...), which fails
    mock_session.execute.side_effect = OperationalError("Simulated session read-only failure", None, None)

    res = execute_read_query("SELECT name FROM students;", session=mock_session)

    assert res["status"] == "error"
    assert "Failed to enforce read-only transaction mode" in res["error"]
    assert res["row_count"] == 0
    # Verify session rollback was called
    mock_session.rollback.assert_called_once()
    # Verify user query was not executed
    assert mock_session.execute.call_count == 1


# ---------------------------------------------------------------------------
# 10. Test Database Target Safeguards
# ---------------------------------------------------------------------------

def test_test_database_target_validation_safeguards():
    """Verify that validate_test_database_target blocks non-test or missing database URLs."""
    from backend.tests.test_postgres_integration import validate_test_database_target

    # 1. Missing URL is rejected
    valid, msg = validate_test_database_target("")
    assert valid is False
    assert "not configured" in msg or "not set" in msg

    # 2. Non-postgres scheme is rejected
    valid, msg = validate_test_database_target("sqlite:///test.db")
    assert valid is False
    assert "must be a PostgreSQL connection URL" in msg

    # 3. Production / application database without 'test' in the name is strictly rejected
    valid, msg = validate_test_database_target("postgresql+psycopg://user:pass@localhost:5432/querymind_db")
    assert valid is False
    assert "Safety violation" in msg
    assert "querymind_db" in msg

    valid, msg = validate_test_database_target("postgresql+psycopg://user:pass@localhost:5432/production_app")
    assert valid is False
    assert "Safety violation" in msg

    # 4. Dedicated test database with 'test' in the name is accepted
    valid, msg = validate_test_database_target("postgresql+psycopg://user:pass@localhost:5432/querymind_test_db")
    assert valid is True
    assert "querymind_test_db" in msg
