"""Pydantic schemas for direct PostgreSQL database retrieval and health endpoints."""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class DatabaseHealthResponse(BaseModel):
    """Schema for GET /api/v1/database/health response."""

    status: str = Field(..., description="Database connection status", examples=["connected"])
    database: str = Field(..., description="Connected database name", examples=["querymind_db"])
    database_type: str = Field(..., description="Database dialect", examples=["postgresql"])


class StudentRecord(BaseModel):
    """Schema for individual student database entity."""

    student_id: int = Field(..., description="Student ID primary key")
    id: int = Field(..., description="Identifier alias matching model PK")
    name: str = Field(..., description="Student full name")
    batch: int = Field(..., description="Cohort or batch graduation year")
    cgpa: float = Field(..., description="Cumulative Grade Point Average")
    department: str = Field(..., description="Academic department code")


class CourseRecord(BaseModel):
    """Schema for individual course database entity."""

    course_id: int = Field(..., description="Course ID primary key")
    id: int = Field(..., description="Identifier alias matching model PK")
    course_name: str = Field(..., description="Course title")
    credits: int = Field(..., description="Credit hours")
    department: str = Field(..., description="Department offering course")


class EnrollmentRecord(BaseModel):
    """Schema for individual enrollment database entity."""

    enrollment_id: int = Field(..., description="Enrollment ID primary key")
    id: int = Field(..., description="Identifier alias matching model PK")
    student_id: int = Field(..., description="Referenced student ID")
    course_id: int = Field(..., description="Referenced course ID")
    semester: str = Field(..., description="Academic semester term")
    grade: Optional[str] = Field(default=None, description="Letter grade awarded")
    student_name: Optional[str] = Field(default=None, description="Joined student name")
    course_name: Optional[str] = Field(default=None, description="Joined course title")


class StudentListResponse(BaseModel):
    """Schema for student list retrieval from PostgreSQL."""

    success: bool = Field(default=True, description="Operation success flag")
    source: str = Field(default="postgresql", description="Data source indicator")
    count: int = Field(..., description="Number of retrieved records")
    data: List[StudentRecord] = Field(..., description="List of student records")


class CourseListResponse(BaseModel):
    """Schema for course list retrieval from PostgreSQL."""

    success: bool = Field(default=True, description="Operation success flag")
    source: str = Field(default="postgresql", description="Data source indicator")
    count: int = Field(..., description="Number of retrieved records")
    data: List[CourseRecord] = Field(..., description="List of course records")


class EnrollmentListResponse(BaseModel):
    """Schema for enrollment list retrieval from PostgreSQL."""

    success: bool = Field(default=True, description="Operation success flag")
    source: str = Field(default="postgresql", description="Data source indicator")
    count: int = Field(..., description="Number of retrieved records")
    data: List[EnrollmentRecord] = Field(..., description="List of enrollment records")

