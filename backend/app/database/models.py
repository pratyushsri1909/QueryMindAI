"""Provisional Academic Domain SQLAlchemy ORM Models for QueryMind AI (Day 3 Foundation).

PROVISIONAL NOTICE:
-------------------
This schema is provisional and developed for Day 3 database foundation, connection
pooling, session management, and read-only query execution verification.
The final database topology, table structures, and indexing strategies will be
confirmed or refined by Member 2 (Database & SQL Engine Engineer) in subsequent milestones.
Application components must remain loosely coupled to these specific definitions.
"""

from typing import List, Optional
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy ORM models."""
    pass


class Student(Base):
    """Represents an academic student entity.

    Table: students
    """

    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, doc="Unique student identifier"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, doc="Full name of student"
    )
    batch: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="Admission or graduation cohort year (e.g. 2028)"
    )
    cgpa: Mapped[float] = mapped_column(
        Float,
        CheckConstraint("cgpa >= 0.0 AND cgpa <= 10.0", name="ck_students_cgpa_range"),
        nullable=False,
        doc="Cumulative Grade Point Average (0.0 to 10.0)",
    )
    department: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="Department abbreviation (e.g. CSE, AI, ECE)"
    )

    # Relationships
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
        doc="Enrollment records associated with this student",
    )

    __table_args__ = (
        Index("ix_students_cgpa", "cgpa"),
        Index("ix_students_department", "department"),
        Index("ix_students_batch", "batch"),
    )

    def __repr__(self) -> str:
        return (
            f"<Student(id={self.student_id}, name='{self.name}', "
            f"batch={self.batch}, cgpa={self.cgpa}, dept='{self.department}')>"
        )


class Course(Base):
    """Represents an academic course offered by a department.

    Table: courses
    """

    __tablename__ = "courses"

    course_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, doc="Unique course identifier"
    )
    course_name: Mapped[str] = mapped_column(
        String(150), nullable=False, doc="Official title of the course"
    )
    credits: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("credits > 0 AND credits <= 10", name="ck_courses_credits_range"),
        nullable=False,
        doc="Number of academic credits",
    )
    department: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="Offering department (e.g. CSE, AI, ECE)"
    )

    # Relationships
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
        doc="Enrollment records associated with this course",
    )

    __table_args__ = (
        Index("ix_courses_department", "department"),
    )

    def __repr__(self) -> str:
        return (
            f"<Course(id={self.course_id}, name='{self.course_name}', "
            f"credits={self.credits}, dept='{self.department}')>"
        )


class Enrollment(Base):
    """Represents a student's enrollment in a course for an academic semester.

    Table: enrollments
    """

    __tablename__ = "enrollments"

    enrollment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, doc="Unique enrollment record ID"
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key referencing students.student_id",
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key referencing courses.course_id",
    )
    semester: Mapped[str] = mapped_column(
        String(30), nullable=False, doc="Academic term (e.g. Fall 2024, Spring 2025)"
    )
    grade: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True, doc="Letter grade earned (e.g. A, B+, A-), or null if in progress"
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student", back_populates="enrollments"
    )
    course: Mapped["Course"] = relationship(
        "Course", back_populates="enrollments"
    )

    __table_args__ = (
        Index("ix_enrollments_student_id", "student_id"),
        Index("ix_enrollments_course_id", "course_id"),
        Index("ix_enrollments_semester", "semester"),
    )

    def __repr__(self) -> str:
        return (
            f"<Enrollment(id={self.enrollment_id}, student_id={self.student_id}, "
            f"course_id={self.course_id}, sem='{self.semester}', grade='{self.grade}')>"
        )

