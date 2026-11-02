"""Mock SQL Engine for QueryMind AI (Day 2 Integration Prototype).

DISCLAIMER:
-----------
This module is a deterministic MOCK implementation designed for Day 2 full-stack
wiring and contract verification. It does NOT connect to PostgreSQL, nor does it
run an AST parser (SQLGlot) or execute dynamic SQL queries on a physical database.
Generated SQL is deterministically constructed from the Intermediate Representation (IR),
and execution results are deterministic static fixture datasets.
The actual schema catalog, AST security validator, and PostgreSQL executor will
be implemented by Member 2 in subsequent project phases.
"""

from typing import Any, Dict, List


# Deterministic mock datasets for Day 2 prototype
MOCK_DATASETS: Dict[str, Dict[str, Any]] = {
    "students_cgpa_filter": {
        "columns": ["name", "cgpa"],
        "rows": [
            ["Aarav", 9.1],
            ["Diya", 8.8],
            ["Kabir", 8.7],
        ],
    },
    "students_sorted": {
        "columns": ["name", "cgpa", "graduation_year"],
        "rows": [
            ["Aarav Sharma", 9.1, 2025],
            ["Diya Patel", 8.8, 2024],
            ["Kabir Mehta", 8.7, 2025],
            ["Rohan Verma", 8.4, 2024],
            ["Ananya Gupta", 8.2, 2025],
        ],
    },
    "courses_filter": {
        "columns": ["course_code", "course_name", "credits"],
        "rows": [
            ["CS101", "Introduction to Computer Science", 4],
            ["CS201", "Data Structures & Algorithms", 4],
            ["CS301", "Database Management Systems", 4],
            ["CS401", "Artificial Intelligence", 4],
        ],
    },
    "default_students": {
        "columns": ["id", "name", "department", "cgpa"],
        "rows": [
            [1, "Aarav Sharma", "Computer Science", 9.1],
            [2, "Diya Patel", "Computer Science", 8.8],
            [3, "Kabir Mehta", "Electrical Engineering", 8.7],
            [4, "Rohan Verma", "Mechanical Engineering", 8.4],
            [5, "Ananya Gupta", "Information Technology", 8.2],
        ],
    },
}


def _build_mock_sql(ir: Dict[str, Any]) -> str:
    """Construct deterministic ANSI SQL from Intermediate Representation (IR).

    Args:
        ir: Intermediate Representation dictionary.

    Returns:
        str: Syntactically valid SQL query string.
    """
    columns = ", ".join(ir.get("columns", ["*"]))
    table = ir.get("table", "students")
    sql = f"SELECT {columns} FROM {table}"

    conditions = ir.get("conditions", [])
    if conditions:
        clause_parts: List[str] = []
        for cond in conditions:
            col = cond.get("column")
            op = cond.get("operator")
            val = cond.get("value")
            # Format numeric vs string literals appropriately
            val_str = str(val) if isinstance(val, (int, float)) else f"'{val}'"
            clause_parts.append(f"{col} {op} {val_str}")
        sql += f" WHERE {' AND '.join(clause_parts)}"

    if ir.get("order_by"):
        sql += f" ORDER BY {ir['order_by']}"

    if ir.get("limit"):
        sql += f" LIMIT {ir['limit']}"

    return f"{sql};"


def process_ir(ir: Dict[str, Any]) -> Dict[str, Any]:
    """Translate an Intermediate Representation (IR) into SQL and return mock execution results.

    Args:
        ir: Intermediate Representation dictionary from the NLP module.

    Returns:
        Dict[str, Any]: Dictionary containing generated_sql and execution metadata/results.
    """
    generated_sql = _build_mock_sql(ir)

    table = ir.get("table", "students")
    intent = ir.get("intent", "SELECT_ALL")
    conditions = ir.get("conditions", [])

    # Match dataset fixture based on IR characteristics
    if table == "students" and conditions and any(c.get("column") == "cgpa" for c in conditions):
        fixture = MOCK_DATASETS["students_cgpa_filter"]
    elif table == "students" and intent == "SORT":
        fixture = MOCK_DATASETS["students_sorted"]
    elif table == "courses":
        fixture = MOCK_DATASETS["courses_filter"]
    else:
        fixture = MOCK_DATASETS["default_students"]

    rows = fixture["rows"]
    columns = fixture["columns"]

    execution_payload = {
        "status": "mock_success",
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "execution_time_ms": 12,
    }

    return {
        "generated_sql": generated_sql,
        "execution": execution_payload,
    }
