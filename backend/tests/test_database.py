"""Automated unit and integration tests for QueryMind AI Day 3 Database Foundation."""

import datetime
import json
import uuid
from decimal import Decimal
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings
from app.database.models import Base, Student, Course, Enrollment
from app.database.session import check_db_connection, get_session_factory, get_engine
from app.database.seed import seed_database
from app.services.database_service import (
    validate_sql,
    execute_read_query,
    _serialize_value,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixture: In-Memory SQLite Test Engine & Session
# ---------------------------------------------------------------------------
@pytest.fixture
def in_memory_db():
    """Create an isolated, transient in-memory SQLite database for ORM testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()
    try:
        yield engine, session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# 1. Database Configuration Tests
# ---------------------------------------------------------------------------
def test_database_configuration_defaults():
    """Verify that default settings instantiate with expected PostgreSQL driver URL and mock mode."""
    cfg = Settings()
    assert "postgresql" in cfg.database_url
    assert cfg.querymind_mode in ("mock", "database")
    assert cfg.db_statement_timeout_ms == 5000


def test_database_configuration_override():
    """Verify that settings accept environment overrides."""
    custom_cfg = Settings(
        database_url="postgresql+psycopg://usr:pwd@dbhost:5432/custom_db",
        querymind_mode="database",
        db_statement_timeout_ms=3000,
    )
    assert custom_cfg.database_url == "postgresql+psycopg://usr:pwd@dbhost:5432/custom_db"
    assert custom_cfg.querymind_mode == "database"
    assert custom_cfg.db_statement_timeout_ms == 3000


# ---------------------------------------------------------------------------
# 2. Provisional ORM Models & Relationships Tests
# ---------------------------------------------------------------------------
def test_orm_models_and_relationships(in_memory_db):
    """Verify provisional Student, Course, and Enrollment models and ORM cascades."""
    engine, session = in_memory_db

    # Create Student & Course
    student = Student(student_id=1, name="Aarav", batch=2028, cgpa=9.1, department="CSE")
    course = Course(course_id=101, course_name="Intro to CS", credits=4, department="CSE")
    session.add_all([student, course])
    session.flush()

    # Create Enrollment linking student and course
    enrollment = Enrollment(
        enrollment_id=1,
        student_id=student.student_id,
        course_id=course.course_id,
        semester="Fall 2024",
        grade="A",
    )
    session.add(enrollment)
    session.commit()

    # Query back & verify relationships
    fetched_student = session.get(Student, 1)
    assert fetched_student is not None
    assert fetched_student.name == "Aarav"
    assert len(fetched_student.enrollments) == 1
    assert fetched_student.enrollments[0].course.course_name == "Intro to CS"


# ---------------------------------------------------------------------------
# 3. Sample Data Seeding Idempotency Tests
# ---------------------------------------------------------------------------
def test_seed_database_idempotency(in_memory_db):
    """Verify that seed_database initializes all sample records and is safely repeatable."""
    engine, session = in_memory_db

    # Initial seed
    counts_first = seed_database(session)
    assert counts_first["students"] == 5
    assert counts_first["courses"] == 5
    assert counts_first["enrollments"] == 9

    # Verify rows in DB
    students = session.query(Student).all()
    assert len(students) == 5
    diya = session.query(Student).filter_by(name="Diya").first()
    assert diya is not None
    assert diya.cgpa == 8.8

    # Re-run seed (must be idempotent without primary key violation)
    counts_second = seed_database(session)
    assert counts_second["students"] == 5
    students_after = session.query(Student).all()
    assert len(students_after) == 5


# ---------------------------------------------------------------------------
# 4. SQL Validation Security Tests
# ---------------------------------------------------------------------------
def test_sql_validation_accepts_valid_read_queries():
    """Verify that valid SELECT queries, joins, and CTEs pass validation."""
    valid_queries = [
        "SELECT name, cgpa FROM students WHERE cgpa > 8.5;",
        "SELECT * FROM courses WHERE department = 'CSE';",
        "SELECT s.name, c.course_name FROM students s JOIN enrollments e ON s.student_id = e.student_id JOIN courses c ON e.course_id = c.course_id;",
        "SELECT department, AVG(cgpa) as avg_cgpa FROM students GROUP BY department ORDER BY avg_cgpa DESC;",
        "WITH cs_students AS (SELECT * FROM students WHERE department = 'CSE') SELECT name, cgpa FROM cs_students;",
    ]
    for q in valid_queries:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Expected valid query for: {q} | Error: {err}"
        assert err is None


def test_sql_validation_rejects_modifying_statements():
    """Verify that INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, and CREATE are strictly rejected."""
    forbidden_queries = [
        ("DROP TABLE students;", "DROP"),
        ("DELETE FROM students WHERE student_id = 1;", "DELETE"),
        ("UPDATE students SET cgpa = 10.0;", "UPDATE"),
        ("INSERT INTO students VALUES (10, 'Hacker', 2028, 9.9, 'CSE');", "INSERT"),
        ("ALTER TABLE students ADD COLUMN is_admin BOOLEAN;", "ALTER"),
        ("CREATE TABLE test_table (id INT);", "CREATE"),
        ("TRUNCATE TABLE students;", "TRUNCATE"),
    ]
    for q, op in forbidden_queries:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected forbidden query for: {q}"
        assert "Security violation" in err


def test_sql_validation_rejects_multiple_statements():
    """Verify that multiple concatenated SQL statements are rejected to prevent injection."""
    stacked_sql = "SELECT * FROM students; DROP TABLE students;"
    is_valid, err = validate_sql(stacked_sql)
    assert is_valid is False
    assert "Multiple SQL statements" in err


def test_sql_validation_rejects_empty_sql():
    """Verify that empty or blank SQL strings are rejected."""
    for empty in ["", "   ", "\n\t  "]:
        is_valid, err = validate_sql(empty)
        assert is_valid is False
        assert "empty" in err.lower()


def test_sql_validation_rejects_restricted_system_tables():
    """Verify that access to sensitive system catalogs like pg_shadow is rejected."""
    for tbl in ["pg_shadow", "pg_authid", "pg_roles", "pg_database"]:
        is_valid, err = validate_sql(f"SELECT * FROM {tbl};")
        assert is_valid is False
        assert "prohibited" in err.lower()


def test_sql_validation_rejects_select_into():
    """Verify that top-level and nested SELECT ... INTO statements are strictly rejected."""
    into_queries = [
        "SELECT * INTO new_table FROM students;",
        "SELECT student_id, name INTO TEMP temp_students FROM students;",
        "WITH cte AS (SELECT * INTO temp_students FROM students) SELECT * FROM cte;",
        "SELECT * FROM (SELECT * INTO temp_students FROM students) s;",
    ]
    for q in into_queries:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected SELECT INTO to be rejected for: {q}"
        assert "SELECT ... INTO" in err or "Security violation" in err


def test_sql_validation_allows_truncate_in_literal_but_rejects_truncate_table():
    """Verify that 'truncate' as a literal string passes, while TRUNCATE statements are blocked."""
    # Legitimate queries with 'truncate' inside string literals must pass
    valid_literal_queries = [
        "SELECT * FROM students WHERE name = 'truncate';",
        "SELECT course_name FROM courses WHERE department = 'CSE' AND course_name LIKE '%truncate%';",
    ]
    for q in valid_literal_queries:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Expected valid query for: {q} | Error: {err}"
        assert err is None

    # Actual TRUNCATE statements must be rejected via AST inspection
    truncate_statements = [
        "TRUNCATE TABLE students;",
        "TRUNCATE students;",
    ]
    for q in truncate_statements:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected TRUNCATE statement to be rejected for: {q}"
        assert "Security violation" in err


def test_sql_validation_rejects_expanded_system_catalogs_and_schemas():
    """Verify that pg_settings, pg_tables, pg_class, pg_proc, and information_schema are rejected."""
    restricted_queries = [
        "SELECT * FROM pg_settings;",
        "SELECT * FROM pg_tables;",
        "SELECT * FROM pg_class;",
        "SELECT * FROM pg_proc;",
        "SELECT * FROM information_schema.tables;",
        "SELECT * FROM information_schema.columns;",
        "SELECT * FROM pg_catalog.pg_class;",
    ]
    for q in restricted_queries:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected restricted catalog query to be rejected for: {q}"
        assert "Security violation" in err
        assert "prohibited" in err.lower()


def test_sql_validation_rejects_administrative_functions():
    """Verify that dangerous administrative and file I/O functions are rejected."""
    dangerous_function_queries = [
        "SELECT pg_sleep(5);",
        "SELECT pg_sleep_for('5 seconds');",
        "SELECT pg_terminate_backend(1234);",
        "SELECT pg_cancel_backend(1234);",
        "SELECT lo_export(1, 'evil.txt');",
        "SELECT pg_read_file('config.json');",
    ]
    for q in dangerous_function_queries:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected dangerous function to be rejected for: {q}"
        assert "Security violation" in err
        assert "administrative function" in err.lower()


def test_sql_validation_comment_handling_and_edge_cases():
    """Verify that legitimate comments, string literals with semicolons, and edge cases parse safely."""
    # 1. SELECT with trailing line comment (both with and without semicolon)
    valid_line_comment = [
        "SELECT name FROM students; -- list students",
        "SELECT name FROM students -- list students",
    ]
    for q in valid_line_comment:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Failed for: {q} | Error: {err}"
        assert err is None

    # 2. SELECT with block comment
    valid_block_comment = [
        "SELECT name FROM students /* student list */;",
        "SELECT name, /* inline comment */ cgpa FROM students;",
    ]
    for q in valid_block_comment:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Failed for: {q} | Error: {err}"
        assert err is None

    # 3. SELECT with comments before the statement (leading comments)
    valid_leading_comment = [
        "-- header line comment\nSELECT name FROM students;",
        "/* header block comment */ SELECT name FROM students;",
        "/* block 1 */ -- line 1\nSELECT name FROM students;",
    ]
    for q in valid_leading_comment:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Failed for: {q} | Error: {err}"
        assert err is None

    # 4. Semicolons inside string literals
    valid_semicolon_literal = [
        "SELECT name FROM students WHERE name = 'Aarav; -- not a comment';",
        "SELECT name FROM students WHERE name = 'semi;colon;test';",
    ]
    for q in valid_semicolon_literal:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Failed for: {q} | Error: {err}"
        assert err is None

    # 5. SQL keywords inside string literals
    valid_keywords_literal = [
        "SELECT * FROM students WHERE name = 'DROP TABLE students; DELETE FROM courses;';",
        "SELECT * FROM courses WHERE course_name = 'INSERT INTO courses VALUES (1);';",
    ]
    for q in valid_keywords_literal:
        is_valid, err = validate_sql(q)
        assert is_valid is True, f"Failed for: {q} | Error: {err}"
        assert err is None

    # 6. Multiple statements with comments between them (must be rejected)
    multiple_with_comments = [
        "SELECT * FROM students; /* comment */ DROP TABLE students;",
        "SELECT * FROM students; -- comment\nDROP TABLE students;",
        "SELECT * FROM students; -- comment\nSELECT * FROM courses;",
    ]
    for q in multiple_with_comments:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected multiple statements to be rejected for: {q}"
        assert "Multiple SQL statements" in err

    # 7. SELECT INTO with comments (must be rejected)
    into_with_comments = [
        "SELECT * INTO new_table FROM students; -- comment",
        "/* comment */ SELECT * INTO new_table FROM students;",
    ]
    for q in into_with_comments:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected SELECT INTO to be rejected for: {q}"
        assert "Security violation" in err

    # 8. Nested forbidden operations with comments (must be rejected)
    forbidden_with_comments = [
        "WITH cte AS (DELETE FROM students RETURNING *) SELECT * FROM cte; -- comment",
        "WITH cte AS (INSERT INTO students VALUES (99, 'X', 2028, 9.0, 'CSE') RETURNING *) SELECT * FROM cte; /* c */",
    ]
    for q in forbidden_with_comments:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected nested forbidden op to be rejected for: {q}"
        assert "Security violation" in err

    # 9. Empty SQL and comment-only SQL (must be rejected)
    empty_and_comment_only = [
        "",
        "   ",
        "\t\n  ",
        "-- comment only",
        "/* block comment only */",
        ";",
        ";;;",
        "; -- trailing comment",
    ]
    for q in empty_and_comment_only:
        is_valid, err = validate_sql(q)
        assert is_valid is False, f"Expected empty/comment-only query to be rejected for: {repr(q)}"
        assert "empty" in err.lower() or "no valid sql" in err.lower()


# ---------------------------------------------------------------------------
# 5. Database Service Execution Tests
# ---------------------------------------------------------------------------
def test_execute_read_query_success(in_memory_db):
    """Verify execute_read_query returns formatted columns, rows, and latency against active engine."""
    engine, session = in_memory_db
    seed_database(session)

    res = execute_read_query("SELECT name, cgpa FROM students WHERE cgpa > 8.5 ORDER BY cgpa DESC;", engine=engine)
    assert res["status"] == "database_success"
    assert res["columns"] == ["name", "cgpa"]
    assert res["row_count"] == 3
    assert len(res["rows"]) == 3
    assert res["rows"][0][0] == "Aarav"
    assert res["rows"][0][1] == 9.1
    assert res["execution_time_ms"] >= 0
    assert res["error"] is None


def test_execute_read_query_validation_rejection():
    """Verify execute_read_query rejects forbidden queries before touching the engine."""
    res = execute_read_query("DROP TABLE students;")
    assert res["status"] == "error"
    assert res["row_count"] == 0
    assert "Security violation" in res["error"]


def test_execute_read_query_runtime_error(in_memory_db):
    """Verify runtime query error (e.g. non-existent table) returns structured error without crashing."""
    engine, session = in_memory_db
    res = execute_read_query("SELECT * FROM non_existent_table_xyz;", engine=engine)
    assert res["status"] == "error"
    assert "Database execution error" in res["error"]


def test_execute_read_query_session_timeout():
    """Verify that statement_timeout cancels long queries executed through a SQLAlchemy Session."""
    conn_info = check_db_connection()
    if not conn_info["connected"]:
        pytest.skip("PostgreSQL database is offline; skipping live session timeout test.")

    session = get_session_factory()()
    try:
        # Deliberately short timeout of 150ms on a 1000ms sleep
        res = execute_read_query(
            "SELECT pg_sleep(1);",
            session=session,
            timeout_ms=150,
            validate=False,
        )
        assert res["status"] == "error"
        assert "statement timeout" in res["error"].lower()

        # Verify that Session transaction is handled safely after cancellation and reusable
        val = session.execute(text("SELECT 1")).scalar()
        assert val == 1
    finally:
        session.close()


def test_execute_read_query_engine_timeout():
    """Verify that statement_timeout cancels long queries executed through an Engine connection."""
    conn_info = check_db_connection()
    if not conn_info["connected"]:
        pytest.skip("PostgreSQL database is offline; skipping live engine timeout test.")

    eng = get_engine()
    res = execute_read_query(
        "SELECT pg_sleep(1);",
        engine=eng,
        timeout_ms=150,
        validate=False,
    )
    assert res["status"] == "error"
    assert "statement timeout" in res["error"].lower()


def test_execute_read_query_parameterized(in_memory_db):
    """Verify that parameterized queries bind named parameters safely, including apostrophes."""
    engine, session = in_memory_db
    seed_database(session)

    # 1. Parameterized filter
    res_param = execute_read_query(
        "SELECT name, cgpa FROM students WHERE cgpa > :minimum_cgpa ORDER BY cgpa DESC;",
        params={"minimum_cgpa": 8.5},
        engine=engine,
    )
    assert res_param["status"] == "database_success"
    assert res_param["row_count"] == 3
    assert res_param["rows"][0][0] == "Aarav"
    assert res_param["rows"][0][1] == 9.1

    # 2. String parameter containing apostrophes (SQL injection attempt)
    res_apostrophe = execute_read_query(
        "SELECT * FROM students WHERE name = :search_name;",
        params={"search_name": "O'Connor'; DROP TABLE students; --"},
        engine=engine,
    )
    assert res_apostrophe["status"] == "database_success"
    assert res_apostrophe["row_count"] == 0

    # 3. Existing callers without parameters continue working (backward compatibility)
    res_no_params = execute_read_query(
        "SELECT name, cgpa FROM students WHERE cgpa > 8.5 ORDER BY cgpa DESC;",
        engine=engine,
    )
    assert res_no_params["status"] == "database_success"
    assert res_no_params["row_count"] == 3


def test_execute_read_query_decimal_serialization():
    """Verify that Decimal aggregate results are converted safely to JSON-compatible types."""
    # Test integer-valued Decimals become int
    assert _serialize_value(Decimal("4.0000")) == 4
    assert isinstance(_serialize_value(Decimal("4.0000")), int)
    assert _serialize_value(Decimal("0.0")) == 0
    assert isinstance(_serialize_value(Decimal("0.0")), int)

    # Test fraction-valued Decimals become float
    assert _serialize_value(Decimal("8.75")) == 8.75
    assert isinstance(_serialize_value(Decimal("8.75")), float)

    # Test primitives and None remain unaltered
    assert _serialize_value("CSE") == "CSE"
    assert _serialize_value(42) == 42
    assert _serialize_value(3.14) == 3.14
    assert _serialize_value(None) is None
    assert _serialize_value(True) is True

    # Test nested structures and JSON serializability
    row = [_serialize_value(Decimal("8.75")), _serialize_value(Decimal("4.00")), "CSE", None]
    json_output = json.dumps(row)
    assert json_output == '[8.75, 4, "CSE", null]'


def test_execute_read_query_date_and_uuid_serialization():
    """Verify that datetime.date, datetime.datetime, datetime.time, and uuid.UUID are formatted safely."""
    sample_date = datetime.date(2026, 11, 11)
    sample_datetime = datetime.datetime(2026, 11, 11, 1, 15, 30)
    sample_time = datetime.time(1, 15, 30)
    sample_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

    assert _serialize_value(sample_date) == "2026-11-11"
    assert _serialize_value(sample_datetime) == "2026-11-11T01:15:30"
    assert _serialize_value(sample_time) == "01:15:30"
    assert _serialize_value(sample_uuid) == "12345678-1234-5678-1234-567812345678"

    # Verify JSON serializability of date and UUID objects
    row = [
        _serialize_value(sample_date),
        _serialize_value(sample_datetime),
        _serialize_value(sample_time),
        _serialize_value(sample_uuid),
    ]
    encoded = json.dumps(row)
    assert "2026-11-11" in encoded
    assert "12345678-1234-5678-1234-567812345678" in encoded


def test_execute_read_query_missing_parameter(in_memory_db):
    """Verify that omitting a required bind parameter fails safely without modifying data."""
    engine, session = in_memory_db
    seed_database(session)

    # Missing named parameter :missing_cgpa
    res = execute_read_query(
        "SELECT * FROM students WHERE cgpa > :missing_cgpa;",
        engine=engine,
    )
    assert res["status"] == "error"
    assert "Database execution error" in res["error"]
    assert "missing_cgpa" in res["error"]
    assert res["row_count"] == 0

    # Verify that database was completely unmodified
    students = session.query(Student).all()
    assert len(students) == 5


def test_execute_read_query_positional_signature_compatibility(in_memory_db):
    """Verify backward compatibility of Day 3 positional parameters (sql, session, engine, timeout_ms)."""
    engine, session = in_memory_db
    seed_database(session)

    # 1. Day 3 positional call: execute_read_query(sql, session, engine, timeout_ms)
    res_pos = execute_read_query(
        "SELECT name, cgpa FROM students WHERE cgpa > 8.5 ORDER BY cgpa DESC;",
        session,
        None,
        5000,
    )
    assert res_pos["status"] == "database_success"
    assert res_pos["row_count"] == 3

    # 2. Positional dict passed as 2nd argument: execute_read_query(sql, params_dict)
    res_dict = execute_read_query(
        "SELECT name, cgpa FROM students WHERE cgpa > :min_cgpa ORDER BY cgpa DESC;",
        {"min_cgpa": 8.5},
        engine=engine,
    )
    assert res_dict["status"] == "database_success"
    assert res_dict["row_count"] == 3


# ---------------------------------------------------------------------------
# 6. Database Connection Failure & Health Check Tests
# ---------------------------------------------------------------------------
def test_check_db_connection_unreachable():
    """Verify check_db_connection returns disconnected status safely when target host is down."""
    # Dummy engine pointing to an unreachable port with 1s timeout
    unreachable_engine = create_engine(
        "postgresql+psycopg://postgres:fake_pwd@127.0.0.1:54329/fake_db",
        connect_args={"connect_timeout": 1},
        pool_timeout=1,
    )
    status_info = check_db_connection(unreachable_engine)
    assert status_info["connected"] is False
    assert status_info["status"] == "disconnected"
    assert status_info["error"] is not None
    # Verify no password leakage in error string
    assert "fake_pwd" not in status_info["error"]


def test_health_endpoint_with_database_flag():
    """Verify GET /health?include_db=true and GET /api/v1/health return database status."""
    res = client.get("/health?include_db=true")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert data["database"] in ("connected", "disconnected")

    # API router health
    res_api = client.get("/api/v1/health")
    assert res_api.status_code == 200
    data_api = res_api.json()
    assert data_api["status"] == "healthy"
    assert "database" in data_api


# ---------------------------------------------------------------------------
# 7. Query API Integration: Mock vs Database Mode
# ---------------------------------------------------------------------------
def test_query_api_default_mock_mode_preserved():
    """Verify that POST /api/v1/query defaults to Day 2 mock pipeline preserving contract."""
    res = client.post("/api/v1/query", json={"query": "Show students with CGPA above 8.5"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["execution"]["status"] == "mock_success"
    assert data["execution"]["row_count"] == 3


def test_query_api_database_mode_offline_handling():
    """Verify that requesting execution_mode='database' when PostgreSQL is offline reports clean status."""
    res = client.post(
        "/api/v1/query",
        json={
            "query": "Show students with CGPA above 8.5",
            "execution_mode": "database",
        },
    )
    assert res.status_code == 200
    data = res.json()
    # Since local PostgreSQL is not running in test env, it handles the offline state cleanly
    if data["execution"]["status"] == "error":
        assert "Database is disconnected" in data["execution"]["error"]
    else:
        assert data["execution"]["status"] == "database_success"


# ---------------------------------------------------------------------------
# 8. Direct PostgreSQL Database Endpoints Tests (/api/v1/database/*)
# ---------------------------------------------------------------------------
def test_api_database_health_success():
    """Verify GET /api/v1/database/health returns 200 and expected schema when connected."""
    res = client.get("/api/v1/database/health")
    # If live PostgreSQL is running, returns 200 with schema keys
    if res.status_code == 200:
        data = res.json()
        assert data["status"] == "connected"
        assert "database" in data
        assert data["database_type"] == "postgresql"
    else:
        # If running in environment without live DB, returns 503
        assert res.status_code == 503
        assert "unavailable" in res.json()["detail"].lower()


def test_api_database_health_failure_returns_503(monkeypatch):
    """Verify GET /api/v1/database/health returns 503 and safe message on connection failure."""
    from sqlalchemy.exc import OperationalError

    def mock_get_engine():
        class FailingEngine:
            @property
            def url(self):
                class MockURL:
                    database = "test_db"
                return MockURL()
            @property
            def dialect(self):
                class MockDialect:
                    name = "postgresql"
                return MockDialect()
            def connect(self):
                raise OperationalError("connection refused to postgres:secret@127.0.0.1:5432", None, None)
        return FailingEngine()

    monkeypatch.setattr("app.api.routes.get_engine", mock_get_engine)

    res = client.get("/api/v1/database/health")
    assert res.status_code == 503
    assert res.json()["detail"] == "PostgreSQL database connection is unavailable."
    # Ensure sensitive credentials are never leaked
    assert "secret" not in str(res.json())


def test_api_database_students_with_override(in_memory_db):
    """Verify GET /api/v1/database/students returns actual records from SQLAlchemy session."""
    from app.database.session import get_db
    engine, session = in_memory_db
    seed_database(session)

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        res = client.get("/api/v1/database/students")
        assert res.status_code == 200
        payload = res.json()
        assert payload["success"] is True
        assert payload["source"] == "postgresql"
        assert payload["count"] == 5
        assert len(payload["data"]) == 5

        # Check first student record structure
        first_student = payload["data"][0]
        assert first_student["name"] == "Aarav"
        assert first_student["cgpa"] == 9.1
        assert first_student["department"] == "CSE"
        assert first_student["student_id"] == 1
        assert first_student["id"] == 1
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_api_database_students_empty_table(in_memory_db):
    """Verify GET /api/v1/database/students returns empty array and count 0 if no records exist."""
    from app.database.session import get_db
    engine, session = in_memory_db

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        res = client.get("/api/v1/database/students")
        assert res.status_code == 200
        payload = res.json()
        assert payload["success"] is True
        assert payload["count"] == 0
        assert payload["data"] == []
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_api_database_courses_with_override(in_memory_db):
    """Verify GET /api/v1/database/courses returns actual course records."""
    from app.database.session import get_db
    engine, session = in_memory_db
    seed_database(session)

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        res = client.get("/api/v1/database/courses")
        assert res.status_code == 200
        payload = res.json()
        assert payload["success"] is True
        assert payload["source"] == "postgresql"
        assert payload["count"] == 5
        assert len(payload["data"]) == 5
        assert payload["data"][0]["course_name"] == "Introduction to Computer Science"
        assert payload["data"][0]["credits"] == 4
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_api_database_enrollments_with_override(in_memory_db):
    """Verify GET /api/v1/database/enrollments returns actual enrollment records with relations."""
    from app.database.session import get_db
    engine, session = in_memory_db
    seed_database(session)

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        res = client.get("/api/v1/database/enrollments")
        assert res.status_code == 200
        payload = res.json()
        assert payload["success"] is True
        assert payload["source"] == "postgresql"
        assert payload["count"] == 9
        assert len(payload["data"]) == 9
        assert payload["data"][0]["semester"] == "Fall 2024"
        assert payload["data"][0]["student_name"] == "Aarav"
        assert payload["data"][0]["course_name"] == "Introduction to Computer Science"
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_api_database_students_error_handling():
    """Verify GET /api/v1/database/students returns 500 when database throws an exception."""
    from app.database.session import get_db
    from sqlalchemy.exc import OperationalError

    def failing_get_db():
        class MockFailingSession:
            def query(self, *args, **kwargs):
                raise OperationalError("SELECT * FROM students failed", None, None)
            def close(self):
                pass
        yield MockFailingSession()

    app.dependency_overrides[get_db] = failing_get_db
    try:
        res = client.get("/api/v1/database/students")
        assert res.status_code == 500
        assert res.json()["detail"] == "Failed to retrieve student records from database."
    finally:
        app.dependency_overrides.pop(get_db, None)
