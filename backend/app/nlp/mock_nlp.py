"""Mock NLP Module for QueryMind AI (Day 2 Integration Prototype).

DISCLAIMER:
-----------
This module is a deterministic MOCK implementation created solely for Day 2
architectural integration, schema verification, and end-to-end pipeline wiring.
It does NOT perform genuine NLP intent classification, machine learning,
tokenization, dependency parsing, or named entity recognition (NER).
Production NLP capabilities will be developed by Member 1 in subsequent milestones.
"""

import re
from typing import Any, Dict


def process_natural_language(query: str) -> Dict[str, Any]:
    """Parse natural language query into an Intermediate Representation (IR).

    This mock implementation employs deterministic pattern matching to simulate
    the NLP pipeline contract agreed upon in the system design specifications (LID).

    Args:
        query: Validated user natural language query string.

    Returns:
        Dict[str, Any]: Intermediate Representation (IR) dictionary conforming
        to the agreed team interface.
    """
    normalized = query.strip().lower()

    # Pattern 1: Queries involving sorting / ranking students by CGPA
    if "student" in normalized and (
        "top" in normalized
        or "order" in normalized
        or "highest" in normalized
        or "rank" in normalized
    ):
        return {
            "intent": "SORT",
            "table": "students",
            "columns": ["name", "cgpa", "graduation_year"],
            "conditions": [],
            "order_by": "cgpa DESC",
            "limit": 5,
        }

    # Pattern 2: Queries involving students and CGPA / GPA filtering
    if "student" in normalized and ("cgpa" in normalized or "gpa" in normalized):
        # Deterministically extract threshold if provided, else default to 8.5
        threshold = 8.5
        match = re.search(
            r"(?:above|greater than|>|higher than|more than)\s*(\d+(?:\.\d+)?)",
            normalized,
        )
        if match:
            try:
                threshold = float(match.group(1))
            except ValueError:
                threshold = 8.5

        return {
            "intent": "FILTER",
            "table": "students",
            "columns": ["name", "cgpa"],
            "conditions": [
                {
                    "column": "cgpa",
                    "operator": ">",
                    "value": threshold,
                }
            ],
            "order_by": None,
            "limit": None,
        }

    # Pattern 3: Queries involving courses and credits
    if "course" in normalized:
        return {
            "intent": "FILTER",
            "table": "courses",
            "columns": ["course_code", "course_name", "credits"],
            "conditions": [
                {
                    "column": "credits",
                    "operator": "=",
                    "value": 4,
                }
            ],
            "order_by": None,
            "limit": None,
        }

    # Generic Fallback: Default deterministic IR for any other input query
    return {
        "intent": "SELECT_ALL",
        "table": "students",
        "columns": ["id", "name", "department", "cgpa"],
        "conditions": [],
        "order_by": None,
        "limit": 10,
    }
