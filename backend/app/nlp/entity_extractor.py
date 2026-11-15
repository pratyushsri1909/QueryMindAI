"""
Entity Extractor for QueryMind AI (Member 1 - NLP Module).
Extracts tables, columns, conditions, joins, aggregations, group_by, order_by, and limits
based on PostgreSQL schema defined in Team Integration Contract Version 1.0.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .schema import DATABASE_SCHEMA, COLUMN_SYNONYMS, SCHEMA_RELATIONSHIPS, OPERATOR_PATTERNS


class EntityExtractor:
    """Extracts schema entities, operators, filters, and structural clauses."""

    def __init__(self):
        self.schema = DATABASE_SCHEMA
        self.column_synonyms = COLUMN_SYNONYMS
        self.relationships = SCHEMA_RELATIONSHIPS

    def extract_table(self, query: str) -> str:
        """Identifies the primary table."""
        query_lower = query.lower()

        # Check explicit table synonyms
        for table, meta in self.schema.items():
            for syn in meta["synonyms"]:
                if re.search(rf"\b{re.escape(syn)}\b", query_lower):
                    return table

        # Check column-based table inference
        for table, col_map in self.column_synonyms.items():
            for col_name, synonyms in col_map.items():
                for syn in synonyms:
                    if re.search(rf"\b{re.escape(syn)}\b", query_lower):
                        return table

        # Default fallback
        return "students"

    def extract_columns(self, query: str, table: str) -> List[str]:
        """Identifies projected columns for the target table."""
        query_lower = query.lower()
        matched_columns = []

        # Find directly mentioned columns
        if table in self.column_synonyms:
            for col_name, synonyms in self.column_synonyms[table].items():
                for syn in synonyms:
                    if re.search(rf"\b{re.escape(syn)}\b", query_lower):
                        if col_name not in matched_columns:
                            matched_columns.append(col_name)

        if not matched_columns:
            # Contextual default columns
            if table == "students":
                matched_columns = ["name", "cgpa"]
            elif table == "courses":
                matched_columns = ["course_name", "credits"]
            else:
                matched_columns = list(self.schema.get(table, {}).get("default_columns", []))
        else:
            # If a metric or secondary column was mentioned, ensure primary identifier is present
            primary_col = "name" if table == "students" else ("course_name" if table == "courses" else None)
            if primary_col and primary_col not in matched_columns:
                matched_columns.insert(0, primary_col)

        return matched_columns

    def extract_conditions(self, query: str, table: str) -> List[Dict[str, Any]]:
        """Extracts conditional WHERE filtering clauses."""
        conditions = []
        query_lower = query.lower()

        # 1. Department condition check: e.g. "from CSE department" or "CSE branch"
        dept_match = re.search(r"\b(?:from|in)\s+([A-Za-z0-9]+)\s+(?:department|dept|branch)\b", query_lower)
        if dept_match:
            dept_val = dept_match.group(1).upper()
            conditions.append({
                "column": "department",
                "operator": "=",
                "value": dept_val
            })

        # 2. General operator-based condition check
        for pattern, op in OPERATOR_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                remainder = query_lower[match.end():].strip()
                # Check for numeric operand
                num_match = re.search(r"^-?\d+(\.\d+)?", remainder)
                if num_match:
                    val_str = num_match.group(0)
                    val = float(val_str) if "." in val_str else int(val_str)

                    # Determine target column
                    target_col = "cgpa"
                    for col_name, synonyms in self.column_synonyms.get(table, {}).items():
                        for syn in synonyms:
                            if syn in query_lower[:match.start()]:
                                target_col = col_name
                                break

                    # Prevent duplicate condition
                    if not any(c["column"] == target_col and c["value"] == val for c in conditions):
                        conditions.append({
                            "column": target_col,
                            "operator": op,
                            "value": val
                        })
                    break

        return conditions

    def extract_aggregations(self, query: str, table: str) -> List[Dict[str, Any]]:
        """Extracts aggregate functions (COUNT, AVG, SUM, MIN, MAX)."""
        aggregations = []
        query_lower = query.lower()

        # COUNT
        if re.search(r"\b(count|how many|number of|total count)\b", query_lower):
            aggregations.append({
                "function": "COUNT",
                "column": "*",
                "alias": "total_count"
            })

        # AVG
        if re.search(r"\b(average|avg|mean)\b", query_lower):
            col = "cgpa" if table == "students" else ("credits" if table == "courses" else "grade")
            aggregations.append({
                "function": "AVG",
                "column": col,
                "alias": f"average_{col}"
            })

        # SUM
        if re.search(r"\b(sum|total credits)\b", query_lower) and not re.search(r"\btotal count\b", query_lower):
            col = "credits" if table == "courses" else "cgpa"
            aggregations.append({
                "function": "SUM",
                "column": col,
                "alias": f"total_{col}"
            })

        # MAX
        if re.search(r"\b(maximum|max|highest marks)\b", query_lower):
            col = "cgpa" if table == "students" else "credits"
            aggregations.append({
                "function": "MAX",
                "column": col,
                "alias": f"max_{col}"
            })

        # MIN
        if re.search(r"\b(minimum|min|lowest marks)\b", query_lower):
            col = "cgpa" if table == "students" else "credits"
            aggregations.append({
                "function": "MIN",
                "column": col,
                "alias": f"min_{col}"
            })

        return aggregations

    def extract_group_by(self, query: str, table: str) -> List[str]:
        """Extracts GROUP BY columns (e.g. 'department-wise', 'by department')."""
        query_lower = query.lower()
        group_by = []

        if re.search(r"\bdepartment[\s-]wise\b|\bby department\b|\bper department\b", query_lower):
            group_by.append("department")
        elif re.search(r"\bcourse[\s-]wise\b|\bby course\b|\bper course\b", query_lower):
            group_by.append("course_id")
        elif re.search(r"\bbatch[\s-]wise\b|\bby batch\b", query_lower):
            group_by.append("batch")

        return group_by

    def extract_order_by(self, query: str, table: str) -> List[Dict[str, str]]:
        """Extracts ORDER BY instructions array."""
        query_lower = query.lower()
        order_by = []
        sort_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "student_id")

        if re.search(r"\b(descending|desc)\b", query_lower) or re.search(r"\btop\s+\d+\b|\bhighest\b|\bbest\b", query_lower):
            order_by.append({
                "column": sort_col,
                "direction": "DESC"
            })
        elif re.search(r"\b(ascending|asc)\b", query_lower) or re.search(r"\bbottom\s+\d+\b|\blowest\b|\bworst\b", query_lower):
            order_by.append({
                "column": sort_col,
                "direction": "ASC"
            })

        return order_by

    def extract_limit(self, query: str) -> Optional[int]:
        """Extracts LIMIT integer."""
        query_lower = query.lower()
        top_match = re.search(r"\b(?:top|first|limit)\s+(\d+)\b", query_lower)
        if top_match:
            return int(top_match.group(1))
        bottom_match = re.search(r"\bbottom\s+(\d+)\b", query_lower)
        if bottom_match:
            return int(bottom_match.group(1))
        return None

    def extract_joins(self, query: str, primary_table: str) -> List[Dict[str, Any]]:
        """Identifies required table joins."""
        query_lower = query.lower()
        joins = []

        # Join detection: students enrolled in courses
        if (
            (primary_table == "students" and ("course" in query_lower or "enrolled" in query_lower or "enrollment" in query_lower)) or
            (primary_table == "courses" and ("student" in query_lower or "enrolled" in query_lower))
        ):
            joins.append({
                "table": "enrollments",
                "type": "INNER",
                "left_column": f"{primary_table}.{primary_table[:-1]}_id" if primary_table.endswith("s") else f"{primary_table}.id",
                "right_column": f"enrollments.{primary_table[:-1]}_id" if primary_table.endswith("s") else f"enrollments.id"
            })

        return joins
