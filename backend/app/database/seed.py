"""Academic sample data seeding script for QueryMind AI (Day 3 Foundation)."""

import logging
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.database.models import Student, Course, Enrollment

logger = logging.getLogger(__name__)

SAMPLE_STUDENTS: List[Dict[str, Any]] = [
    {"student_id": 1, "name": "Aarav", "batch": 2028, "cgpa": 9.1, "department": "CSE"},
    {"student_id": 2, "name": "Diya", "batch": 2028, "cgpa": 8.8, "department": "AI"},
    {"student_id": 3, "name": "Kabir", "batch": 2027, "cgpa": 8.7, "department": "CSE"},
    {"student_id": 4, "name": "Meera", "batch": 2028, "cgpa": 8.2, "department": "AI"},
    {"student_id": 5, "name": "Rohan", "batch": 2027, "cgpa": 7.9, "department": "ECE"},
]

SAMPLE_COURSES: List[Dict[str, Any]] = [
    {"course_id": 101, "course_name": "Introduction to Computer Science", "credits": 4, "department": "CSE"},
    {"course_id": 102, "course_name": "Data Structures & Algorithms", "credits": 4, "department": "CSE"},
    {"course_id": 103, "course_name": "Foundations of Artificial Intelligence", "credits": 3, "department": "AI"},
    {"course_id": 104, "course_name": "Digital Electronics", "credits": 3, "department": "ECE"},
    {"course_id": 105, "course_name": "Database Management Systems", "credits": 4, "department": "CSE"},
]

SAMPLE_ENROLLMENTS: List[Dict[str, Any]] = [
    {"enrollment_id": 1, "student_id": 1, "course_id": 101, "semester": "Fall 2024", "grade": "A"},
    {"enrollment_id": 2, "student_id": 1, "course_id": 105, "semester": "Spring 2025", "grade": "A+"},
    {"enrollment_id": 3, "student_id": 2, "course_id": 103, "semester": "Fall 2024", "grade": "A"},
    {"enrollment_id": 4, "student_id": 2, "course_id": 102, "semester": "Spring 2025", "grade": "A"},
    {"enrollment_id": 5, "student_id": 3, "course_id": 105, "semester": "Fall 2024", "grade": "B+"},
    {"enrollment_id": 6, "student_id": 3, "course_id": 102, "semester": "Fall 2024", "grade": "A"},
    {"enrollment_id": 7, "student_id": 4, "course_id": 103, "semester": "Fall 2024", "grade": "B"},
    {"enrollment_id": 8, "student_id": 4, "course_id": 101, "semester": "Fall 2024", "grade": "A"},
    {"enrollment_id": 9, "student_id": 5, "course_id": 104, "semester": "Fall 2024", "grade": "A-"},
]


def seed_database(session: Session) -> Dict[str, int]:
    """Idempotently seed the provisional academic database with sample data.

    Ensures that re-running the seed operation updates existing entities
    or skips duplicates without raising unique constraint errors.

    Args:
        session: Active SQLAlchemy database session.

    Returns:
        Dict[str, int]: Counts of seeded entities.
    """
    students_count = 0
    courses_count = 0
    enrollments_count = 0

    # 1. Seed Students
    for s_data in SAMPLE_STUDENTS:
        existing = session.get(Student, s_data["student_id"])
        if not existing:
            student = Student(**s_data)
            session.add(student)
            students_count += 1
        else:
            # Update attributes idempotently
            for k, v in s_data.items():
                setattr(existing, k, v)
            students_count += 1

    session.flush()

    # 2. Seed Courses
    for c_data in SAMPLE_COURSES:
        existing = session.get(Course, c_data["course_id"])
        if not existing:
            course = Course(**c_data)
            session.add(course)
            courses_count += 1
        else:
            for k, v in c_data.items():
                setattr(existing, k, v)
            courses_count += 1

    session.flush()

    # 3. Seed Enrollments
    for e_data in SAMPLE_ENROLLMENTS:
        existing = session.get(Enrollment, e_data["enrollment_id"])
        if not existing:
            enrollment = Enrollment(**e_data)
            session.add(enrollment)
            enrollments_count += 1
        else:
            for k, v in e_data.items():
                setattr(existing, k, v)
            enrollments_count += 1

    session.commit()
    logger.info(
        "Seeding complete: %d students, %d courses, %d enrollments.",
        students_count,
        courses_count,
        enrollments_count,
    )

    return {
        "students": students_count,
        "courses": courses_count,
        "enrollments": enrollments_count,
    }


if __name__ == "__main__":
    from app.database.session import get_db, get_engine
    from app.database.init_db import init_database

    print("Initializing database tables...")
    init_database()

    print("Seeding sample academic data...")
    session_gen = get_db()
    db = next(session_gen)
    try:
        counts = seed_database(db)
        print(f"Database seeded successfully: {counts}")
    finally:
        session_gen.close()

