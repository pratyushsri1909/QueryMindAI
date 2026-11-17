"""PostgreSQL end-to-end integration tests for QueryMind AI.

Requires a live PostgreSQL database instance configured via DATABASE_URL or TEST_DATABASE_URL.
In CI, this runs against a dedicated PostgreSQL service container.
When running locally without PostgreSQL available, tests cleanly skip with an informative reason.
"""

import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database.models import Base, Student, Course, Enrollment
from app.services.database_service import execute_read_query, validate_sql

# Resolve test database URL
TEST_DB_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL") or ""


def is_postgres_live() -> bool:
    """Check if PostgreSQL is reachable at TEST_DB_URL."""
    if not TEST_DB_URL or "postgres" not in TEST_DB_URL.lower():
        return False
    try:
        engine = create_engine(TEST_DB_URL, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


# Skip the entire module if PostgreSQL is not available
pytestmark = pytest.mark.skipif(
    not is_postgres_live(),
    reason="Live PostgreSQL database not reachable. Skipping real PostgreSQL integration tests.",
)


@pytest.fixture(scope="module")
def postgres_engine():
    """Create a module-scoped SQLAlchemy engine for PostgreSQL integration testing."""
    engine = create_engine(TEST_DB_URL, echo=False)
    # Ensure fresh schema tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed controlled integration test fixtures
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        students = [
            Student(student_id=1, name="Aarav Sharma", batch=2024, cgpa=9.1, department="CSE"),
            Student(student_id=2, name="Diya Patel", batch=2024, cgpa=8.8, department="AI"),
            Student(student_id=3, name="Kabir Verma", batch=2025, cgpa=8.7, department="CSE"),
            Student(student_id=4, name="Meera Nair", batch=2025, cgpa=8.2, department="AI"),
            Student(student_id=5, name="Rohan Gupta", batch=2024, cgpa=7.9, department="ECE"),
        ]
        courses = [
            Course(course_id=101, course_name="Database Systems", credits=4, department="CSE"),
            Course(course_id=102, course_name="Natural Language Processing", credits=3, department="AI"),
            Course(course_id=103, course_name="Data Structures", credits=4, department="CSE"),
        ]
        enrollments = [
            Enrollment(enrollment_id=1, student_id=1, course_id=101, semester="Fall 2024", grade="A"),
            Enrollment(enrollment_id=2, student_id=1, course_id=102, semester="Fall 2024", grade="A-"),
            Enrollment(enrollment_id=3, student_id=2, course_id=101, semester="Fall 2024", grade="B+"),
            Enrollment(enrollment_id=4, student_id=3, course_id=103, semester="Spring 2025", grade="A"),
        ]
        session.add_all(students + courses + enrollments)
        session.commit()
    finally:
        session.close()

    yield engine

    # Cleanup tables on teardown
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    engine.dispose()


def test_postgres_parameterized_select(postgres_engine):
    """Verify live PostgreSQL execution of filtered query with bound parameters."""
    res = execute_read_query(
        "SELECT name, cgpa, department FROM students WHERE cgpa > :min_cgpa ORDER BY cgpa DESC;",
        params={"min_cgpa": 8.5},
        engine=postgres_engine,
    )
    assert res["status"] == "database_success"
    assert res["row_count"] == 3
    assert res["columns"] == ["name", "cgpa", "department"]
    assert res["rows"][0][0] == "Aarav Sharma"
    assert res["rows"][0][1] == 9.1
    assert res["rows"][1][0] == "Diya Patel"
    assert res["rows"][2][0] == "Kabir Verma"


def test_postgres_multihop_join_query(postgres_engine):
    """Verify live PostgreSQL 3-table JOIN query across students, enrollments, and courses."""
    sql = (
        "SELECT s.name AS student_name, c.course_name, e.grade, e.semester "
        "FROM students s "
        "INNER JOIN enrollments e ON s.student_id = e.student_id "
        "INNER JOIN courses c ON e.course_id = c.course_id "
        "WHERE s.department = :dept "
        "ORDER BY s.name ASC, c.course_name ASC;"
    )
    res = execute_read_query(sql, params={"dept": "CSE"}, engine=postgres_engine)
    assert res["status"] == "database_success"
    assert res["row_count"] == 3
    assert res["columns"] == ["student_name", "course_name", "grade", "semester"]
    # Aarav Sharma enrolled in Database Systems
    first_row = res["rows"][0]
    assert first_row[0] == "Aarav Sharma"
    assert first_row[1] == "Database Systems"
    assert first_row[2] == "A"


def test_postgres_aggregations_and_grouping(postgres_engine):
    """Verify live PostgreSQL aggregate calculations (COUNT, AVG, MIN, MAX)."""
    sql = (
        "SELECT department, COUNT(*) AS student_count, ROUND(AVG(cgpa)::numeric, 2) AS avg_cgpa "
        "FROM students "
        "GROUP BY department "
        "ORDER BY department ASC;"
    )
    res = execute_read_query(sql, engine=postgres_engine)
    assert res["status"] == "database_success"
    assert res["row_count"] == 3
    # AI: 2 students (Diya 8.8, Meera 8.2 -> avg 8.5)
    # CSE: 2 students (Aarav 9.1, Kabir 8.7 -> avg 8.9)
    # ECE: 1 student (Rohan 7.9)
    dept_map = {row[0]: (row[1], float(row[2])) for row in res["rows"]}
    assert dept_map["AI"] == (2, 8.5)
    assert dept_map["CSE"] == (2, 8.9)
    assert dept_map["ECE"] == (1, 7.9)


def test_postgres_write_mutation_rejected_by_validator(postgres_engine):
    """Verify that INSERT/UPDATE/DELETE queries are blocked before reaching PostgreSQL."""
    mutations = [
        "INSERT INTO students (student_id, name, cgpa, department, batch) VALUES (99, 'Hacker', 10.0, 'CSE', 2024);",
        "UPDATE students SET cgpa = 10.0 WHERE student_id = 1;",
        "DELETE FROM students WHERE student_id = 1;",
        "DROP TABLE students;",
    ]
    for sql in mutations:
        res = execute_read_query(sql, engine=postgres_engine)
        assert res["status"] == "error"
        assert "Security violation" in res["error"]

    # Verify that data in PostgreSQL remains unchanged
    check = execute_read_query("SELECT COUNT(*) FROM students;", engine=postgres_engine)
    assert check["rows"][0][0] == 5


def test_postgres_readonly_transaction_enforcement(postgres_engine):
    """Verify that PostgreSQL rejects mutations at the transaction level when validator is bypassed."""
    # Using validate=False to test database transaction-level read-only guardrail
    res = execute_read_query(
        "UPDATE students SET cgpa = 10.0 WHERE student_id = 1;",
        engine=postgres_engine,
        validate=False,
    )
    assert res["status"] == "error"
    err_lower = res["error"].lower()
    assert "read-only" in err_lower or "cannot execute" in err_lower

    # Verify student data remained untouched
    val = execute_read_query(
        "SELECT cgpa FROM students WHERE student_id = 1;",
        engine=postgres_engine,
    )
    assert val["rows"][0][0] == 9.1


def test_postgres_restricted_role_permission_boundary(postgres_engine):
    """Verify that a least-privilege PostgreSQL role can SELECT but cannot mutate data."""
    role_name = "querymind_test_readonly_app"
    role_pass = "app_readonly_secret_123"

    with postgres_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f"DROP ROLE IF EXISTS {role_name};"))
        conn.execute(text(
            f"CREATE ROLE {role_name} WITH LOGIN PASSWORD '{role_pass}' "
            "NOSUPERUSER NOCREATEDB NOCREATEROLE;"
        ))
        conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {role_name};"))
        conn.execute(text(f"GRANT SELECT ON students, courses, enrollments TO {role_name};"))
        conn.execute(text(f"REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON students, courses, enrollments FROM {role_name};"))

    # Connect as the restricted role
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(TEST_DB_URL)
    netloc = f"{role_name}:{role_pass}@{parsed.hostname or 'localhost'}:{parsed.port or 5432}"
    ro_url = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))

    ro_engine = create_engine(ro_url)
    try:
        # 1. SELECT query must succeed
        res = execute_read_query("SELECT name, cgpa FROM students;", engine=ro_engine)
        assert res["status"] == "database_success"
        assert res["row_count"] == 5

        # 2. Direct INSERT attempt bypassing application validation must fail at database level
        res_write = execute_read_query(
            "INSERT INTO students (student_id, name, cgpa, department, batch) VALUES (999, 'Bad', 0.0, 'CSE', 2024);",
            engine=ro_engine,
            validate=False,
        )
        assert res_write["status"] == "error"
        assert "permission denied" in res_write["error"].lower()

    finally:
        ro_engine.dispose()
        with postgres_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text(f"DROP ROLE IF EXISTS {role_name};"))
