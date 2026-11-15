"""
Schema Catalog for QueryMind AI (Member 1 - NLP Engine).
Defines known database tables, columns, data types, and domain-specific synonyms.
"""

from typing import Dict, List, Any

# College database schema definition
SCHEMA_CATALOG: Dict[str, Dict[str, Any]] = {
    "students": {
        "columns": {
            "id": "INTEGER",
            "name": "VARCHAR",
            "cgpa": "FLOAT",
            "email": "VARCHAR",
            "department_id": "INTEGER",
            "admission_year": "INTEGER"
        },
        "default_columns": ["name", "cgpa"],
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
            "department_id": "INTEGER"
        },
        "default_columns": ["course_name", "credits"],
        "synonyms": [
            "course", "courses", "subject", "subjects", "class", "classes",
            "module", "modules", "curriculum"
        ]
    },
    "departments": {
        "columns": {
            "dept_id": "INTEGER",
            "dept_name": "VARCHAR",
            "building": "VARCHAR"
        },
        "default_columns": ["dept_name", "building"],
        "synonyms": [
            "department", "departments", "dept", "depts", "branch", "branches",
            "stream", "faculty"
        ]
    },
    "enrollments": {
        "columns": {
            "enrollment_id": "INTEGER",
            "student_id": "INTEGER",
            "course_id": "INTEGER",
            "grade": "VARCHAR",
            "semester": "INTEGER"
        },
        "default_columns": ["enrollment_id", "student_id", "course_id", "grade"],
        "synonyms": [
            "enrollment", "enrollments", "registration", "registrations",
            "grade", "grades", "score", "scores", "enrolled"
        ]
    }
}

# Column synonym and semantic aliases mapping
COLUMN_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    "students": {
        "cgpa": ["cgpa", "gpa", "marks", "grade point", "score", "percentage", "pointer"],
        "name": ["name", "student name", "full name", "title"],
        "id": ["id", "roll", "roll number", "student id", "registration number"],
        "email": ["email", "mail", "email address", "contact"],
        "admission_year": ["year", "batch", "admission year", "joining year", "intake"],
        "department_id": ["department", "dept", "branch", "stream"]
    },
    "courses": {
        "course_id": ["id", "course code", "code", "course id"],
        "course_name": ["name", "course name", "subject name", "title", "subject"],
        "credits": ["credit", "credits", "points", "weightage", "credit hours"],
        "department_id": ["department", "dept", "branch"]
    },
    "departments": {
        "dept_id": ["id", "dept id", "code"],
        "dept_name": ["name", "department name", "branch name", "stream"],
        "building": ["building", "block", "location", "hall"]
    },
    "enrollments": {
        "grade": ["grade", "mark", "grade letter", "score"],
        "semester": ["semester", "sem", "term"]
    }
}

# Relational operator linguistic patterns
OPERATOR_PATTERNS = [
    (r"\bgreater than or equal to\b|\bat least\b|\bminimum of\b|>=", ">="),
    (r"\bless than or equal to\b|\bat most\b|\bmaximum of\b|<=", "<="),
    (r"\bgreater than\b|\bmore than\b|\babove\b|\bhigher than\b|\bexceeding\b|>", ">"),
    (r"\bless than\b|\bfewer than\b|\bbelow\b|\blower than\b|\bunder\b|<", "<"),
    (r"\bnot equal to\b|\bnot equals\b|\bnot\b|!=|<>", "!="),
    (r"\bequal to\b|\bequals\b|\bis equal to\b|\bis\b|=", "="),
    (r"\bstarts with\b|\bstarting with\b", "LIKE_PREFIX"),
    (r"\bends with\b|\bending with\b", "LIKE_SUFFIX"),
    (r"\bcontains\b|\bcontaining\b|\blike\b", "LIKE")
]
