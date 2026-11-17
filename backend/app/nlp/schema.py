"""
Schema and Knowledge Base for QueryMind AI (Member 1 - NLP Module).
Adheres strictly to Team Integration Contract Version 1.0 (Section 7 Database Schema).
"""

from typing import Dict, List, Any

# PostgreSQL Database Schema definition from Contract Section 7
DATABASE_SCHEMA: Dict[str, Dict[str, Any]] = {
    "students": {
        "columns": {
            "student_id": "INTEGER",
            "name": "VARCHAR",
            "batch": "INTEGER",
            "cgpa": "FLOAT",
            "department": "VARCHAR"
        },
        "default_columns": ["student_id", "name", "cgpa", "department"],
        "synonyms": [
            "student", "students", "pupil", "pupils", "scholar", "scholars",
            "candidate", "candidates", "undergrad", "undergrads"
        ]
    },
    "courses": {
        "columns": {
            "course_id": "INTEGER",
            "course_name": "VARCHAR",
            "credits": "INTEGER",
            "department": "VARCHAR"
        },
        "default_columns": ["course_id", "course_name", "credits", "department"],
        "synonyms": [
            "course", "courses", "subject", "subjects", "class", "classes",
            "module", "modules", "curriculum"
        ]
    },
    "enrollments": {
        "columns": {
            "enrollment_id": "INTEGER",
            "student_id": "INTEGER",
            "course_id": "INTEGER",
            "semester": "VARCHAR",
            "grade": "VARCHAR"
        },
        "default_columns": ["enrollment_id", "student_id", "course_id", "semester", "grade"],
        "synonyms": [
            "enrollment", "enrollments", "registration", "registrations",
            "enrolled", "enroll", "grades", "grade"
        ]
    }
}

# Column synonyms and semantic aliases
COLUMN_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    "students": {
        "student_id": ["id", "student_id", "roll", "roll number", "student id"],
        "name": ["name", "student name", "full name"],
        "batch": ["batch", "year", "admission year", "class of"],
        "cgpa": ["cgpa", "gpa", "marks", "score", "grade point", "percentage", "pointer"],
        "department": ["department", "dept", "branch", "stream", "cse", "ece", "me", "civil"]
    },
    "courses": {
        "course_id": ["course_id", "course id", "code", "course code", "subject id"],
        "course_name": ["course_name", "course name", "name", "subject", "subject name", "title"],
        "credits": ["credit", "credits", "points", "hours", "weightage"],
        "department": ["department", "dept", "branch"]
    },
    "enrollments": {
        "enrollment_id": ["enrollment_id", "enrollment id", "reg id"],
        "student_id": ["student_id", "student id"],
        "course_id": ["course_id", "course id"],
        "semester": ["semester", "sem", "term"],
        "grade": ["grade", "marks", "letter grade"]
    }
}

# Known foreign key join relations (Section 7)
SCHEMA_RELATIONSHIPS = [
    {
        "left_table": "students",
        "right_table": "enrollments",
        "left_column": "students.student_id",
        "right_column": "enrollments.student_id",
        "type": "INNER"
    },
    {
        "left_table": "courses",
        "right_table": "enrollments",
        "left_column": "courses.course_id",
        "right_column": "enrollments.course_id",
        "type": "INNER"
    }
]

# Operator patterns
OPERATOR_PATTERNS = [
    (r"\bgreater than or equal to\b|\bat least\b|\bminimum of\b|>=", ">="),
    (r"\bless than or equal to\b|\bat most\b|\bmaximum of\b|<=", "<="),
    (r"\bgreater than\b|\babove\b|\bmore than\b|\bhigher than\b|\bexceeding\b|>", ">"),
    (r"\bless than\b|\bbelow\b|\bfewer than\b|\blower than\b|\bunder\b|<", "<"),
    (r"\bnot equal to\b|\bnot equals\b|\bnot\b|!=|<>", "!="),
    (r"\bequal to\b|\bequals\b|\bis\b|\bfrom\b|\bin\b|=", "="),
    (r"\bstarts with\b|\bstarting with\b", "LIKE_PREFIX"),
    (r"\bends with\b|\bending with\b", "LIKE_SUFFIX"),
    (r"\bcontains\b|\blike\b", "LIKE")
]
