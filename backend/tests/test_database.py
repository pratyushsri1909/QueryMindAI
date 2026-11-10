"""Automated unit and integration tests for QueryMind AI Day 3 Database Foundation."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings
from app.database.models import Base, Student, Course, Enrollment
from app.database.session import check_db_connection
from app.database.seed import seed_database
from app.services.database_service import validate_sql, execute_read_query

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
