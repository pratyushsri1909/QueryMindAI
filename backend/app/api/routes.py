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
from app.nlp import process_natural_language as process_live_nlp
from app.nlp.mock_nlp import process_natural_language as process_mock_nlp
from app.sql_engine import process_ir as generate_live_sql
from app.sql_engine.mock_sql_engine import process_ir as generate_mock_sql
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
# Natural Language Query Pipeline Endpoint (Mock and Live Database Modes)
# ---------------------------------------------------------------------------
@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Natural Language Query",
    description=(
        "Transforms a natural-language query into an IR, generates SQL, and "
        "executes it in mock or PostgreSQL database mode."
    ),
)
def handle_query(request: QueryRequest) -> QueryResponse:
    # Run the mock prototype or the real NLP -> SQL -> PostgreSQL pipeline.
    try:
        raw_query = request.query
        effective_mode = (
            request.execution_mode or settings.querymind_mode
        ).strip().lower()

        if effective_mode not in {"mock", "database"}:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Server configuration error: QUERYMIND_MODE must be "
                    "'mock' or 'database'."
                ),
            )

        if effective_mode == "mock":
            # Keep the deterministic offline demo working.
            ir = process_mock_nlp(raw_query)
            engine_result = generate_mock_sql(ir)
            generated_sql = engine_result["generated_sql"]
            sql_params: Dict[str, Any] = {}
            execution_payload = engine_result["execution"]
        else:
            # Database mode uses the real canonical NLP and SQL modules.
            ir = process_live_nlp(raw_query)
            if ir.get("success") is False:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=ir.get("error") or {
                        "code": "INVALID_IR",
                        "message": "The NLP module could not interpret this query.",
                    },
                )

            engine_result = generate_live_sql(ir)
            if engine_result.get("success") is not True:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=engine_result.get("error") or {
                        "code": "SQL_GENERATION_FAILED",
                        "message": "The SQL engine could not generate a safe query.",
                    },
                )

            generated_sql = engine_result["generated_sql"]
            sql_params = engine_result.get("params", {})
            # Values remain separate from SQL text. The execution service
            # validates the SQL with SQLGlot before executing it.
            execution_payload = execute_read_query(
                generated_sql,
                params=sql_params,
            )
            # If database execution failed due to connection failure, normalize message
            if execution_payload.get("status") == "error":
                err = execution_payload.get("error") or ""
                if "connection" in err.lower() or "timeout" in err.lower() or "refused" in err.lower() or "permission denied" in err.lower():
                    execution_payload["error"] = f"Database is disconnected ({err})"

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
            params=sql_params,
            execution=execution_payload,
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in query processing pipeline")
        # Keep stack traces in server logs; do not expose internals to clients.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred during query processing.",
        )
