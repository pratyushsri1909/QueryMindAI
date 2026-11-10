"""API routes for natural language query processing and PostgreSQL database foundation."""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.schemas.query import QueryRequest, QueryResponse
from app.schemas.database import (
    DatabaseHealthResponse,
    StudentListResponse,
    StudentRecord,
    CourseListResponse,
    CourseRecord,
    EnrollmentListResponse,
    EnrollmentRecord,
)
from app.nlp.mock_nlp import process_natural_language
from app.sql_engine.mock_sql_engine import process_ir
from app.database.session import get_db, get_engine, check_db_connection
from app.database.models import Student, Course, Enrollment
from app.services.database_service import execute_read_query

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Query Engine"])


# ---------------------------------------------------------------------------
# General API & Service Health Endpoints
# ---------------------------------------------------------------------------
@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="API & Database Health Status",
    description="Returns API service health along with live database connection status.",
)
def api_health() -> Dict[str, Any]:
    """Check API operational status and PostgreSQL database reachability."""
    db_check = check_db_connection()
    return {
        "status": "healthy",
        "database": db_check["status"],
        "dialect": db_check.get("dialect", "postgresql"),
    }


# ---------------------------------------------------------------------------
# Real PostgreSQL Database Endpoints (Day 3 Foundation)
# ---------------------------------------------------------------------------
@router.get(
    "/database/health",
    response_model=DatabaseHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="PostgreSQL Connection Health Check",
    description="Validates live PostgreSQL connectivity using a lightweight SELECT 1 query.",
)
def database_health() -> DatabaseHealthResponse:
    """Check PostgreSQL database connection and return metadata."""
    try:
        eng = get_engine()
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))

        db_name = eng.url.database or "querymind_db"
        db_type = eng.dialect.name

        return DatabaseHealthResponse(
            status="connected",
            database=db_name,
            database_type=db_type,
        )
    except SQLAlchemyError as exc:
        logger.error("PostgreSQL health check failed: %s", str(exc).splitlines()[0])
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL database connection is unavailable.",
        )
    except Exception as exc:
        logger.exception("Unexpected error in database health check: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service error.",
        )


@router.get(
    "/database/students",
    response_model=StudentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Seeded Students",
    description="Fetches actual student records directly from PostgreSQL via SQLAlchemy ORM.",
)
def get_students(db: Session = Depends(get_db)) -> StudentListResponse:
    """Retrieve all student records from PostgreSQL database."""
    try:
        students: List[Student] = db.query(Student).order_by(Student.student_id).all()
        records = [
            StudentRecord(
                student_id=st.student_id,
                id=st.student_id,
                name=st.name,
                batch=st.batch,
                cgpa=st.cgpa,
                department=st.department,
            )
            for st in students
        ]
        return StudentListResponse(
            success=True,
            source="postgresql",
            count=len(records),
            data=records,
        )
    except SQLAlchemyError as exc:
        logger.error("Database query error retrieving students: %s", str(exc).splitlines()[0])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve student records from database.",
        )


@router.get(
    "/database/courses",
    response_model=CourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Seeded Courses",
    description="Fetches actual course records directly from PostgreSQL via SQLAlchemy ORM.",
)
def get_courses(db: Session = Depends(get_db)) -> CourseListResponse:
    """Retrieve all course records from PostgreSQL database."""
    try:
        courses: List[Course] = db.query(Course).order_by(Course.course_id).all()
        records = [
            CourseRecord(
                course_id=c.course_id,
                id=c.course_id,
                course_name=c.course_name,
                credits=c.credits,
                department=c.department,
            )
            for c in courses
        ]
        return CourseListResponse(
            success=True,
            source="postgresql",
            count=len(records),
            data=records,
        )
    except SQLAlchemyError as exc:
        logger.error("Database query error retrieving courses: %s", str(exc).splitlines()[0])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course records from database.",
        )


@router.get(
    "/database/enrollments",
    response_model=EnrollmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Seeded Enrollments",
    description="Fetches actual enrollment records directly from PostgreSQL with joined relations.",
)
def get_enrollments(db: Session = Depends(get_db)) -> EnrollmentListResponse:
    """Retrieve all enrollment records from PostgreSQL database."""
    try:
        enrollments: List[Enrollment] = (
            db.query(Enrollment)
            .options(joinedload(Enrollment.student), joinedload(Enrollment.course))
            .order_by(Enrollment.enrollment_id)
            .all()
        )
        records = [
            EnrollmentRecord(
                enrollment_id=e.enrollment_id,
                id=e.enrollment_id,
                student_id=e.student_id,
                course_id=e.course_id,
                semester=e.semester,
                grade=e.grade,
                student_name=e.student.name if e.student else None,
                course_name=e.course.course_name if e.course else None,
            )
            for e in enrollments
        ]
        return EnrollmentListResponse(
            success=True,
            source="postgresql",
            count=len(records),
            data=records,
        )
    except SQLAlchemyError as exc:
        logger.error("Database query error retrieving enrollments: %s", str(exc).splitlines()[0])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enrollment records from database.",
        )


# ---------------------------------------------------------------------------
# Natural Language Query Pipeline Endpoint (Day 2 Mock / Day 3 DB Routing)
# ---------------------------------------------------------------------------
@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Natural Language Query",
    description=(
        "Transforms a natural language query via NLP into an Intermediate Representation (IR), "
        "synthesizes SQL, and executes it via the configured mode (mock or PostgreSQL database)."
    ),
)
def handle_query(request: QueryRequest) -> QueryResponse:
    """End-to-end integration pipeline endpoint for natural language query processing."""
    try:
        # Step 1: Input query is validated by Pydantic QueryRequest
        raw_query = request.query
        effective_mode = request.execution_mode or settings.querymind_mode

        # Step 2: NLP module processing (mock implementation)
        ir = process_natural_language(raw_query)

        # Step 3: SQL generation from IR
        engine_result = process_ir(ir)
        generated_sql = engine_result["generated_sql"]

        # Step 4: Execution routing based on effective mode
        if effective_mode == "database":
            db_conn = check_db_connection()
            if not db_conn["connected"]:
                execution_payload = {
                    "status": "error",
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time_ms": 0,
                    "error": (
                        f"Database is disconnected ({db_conn['error'] or 'Connection refused'}). "
                        "Ensure PostgreSQL is running and DATABASE_URL is configured."
                    ),
                }
            else:
                execution_payload = execute_read_query(generated_sql)
        else:
            # Default: Day 2 deterministic mock execution
            execution_payload = engine_result["execution"]

        # Step 5: Assemble and return QueryResponse
        return QueryResponse(
            success=execution_payload.get("status") != "error",
            message=(
                "Query processed successfully"
                if execution_payload.get("status") != "error"
                else f"Execution failed: {execution_payload.get('error')}"
            ),
            original_query=raw_query,
            intent=ir.get("intent", "UNKNOWN"),
            ir=ir,
            generated_sql=generated_sql,
            execution=execution_payload,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error in query processing pipeline: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred during query processing: {str(exc)}",
        ) from exc
