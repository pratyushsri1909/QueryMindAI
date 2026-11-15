"""
Entity and Slot Extractor for QueryMind AI (Member 1 - NLP Engine).
Extracts:
- Table entity
- Projection columns
- Predicate conditions (column, operator, value)
- Aggregation functions (AVG, SUM, MIN, MAX, COUNT)
- Order by direction and limit
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .schema_catalog import SCHEMA_CATALOG, COLUMN_SYNONYMS, OPERATOR_PATTERNS


class EntityExtractor:
    """Extracts database schema entities, conditions, limits, and order specifications."""

    def __init__(self):
        self.catalog = SCHEMA_CATALOG
        self.column_synonyms = COLUMN_SYNONYMS

    def extract_table(self, query: str, lemmas: List[str]) -> str:
        """
        Resolves the primary database table name.
        Uses lemma matches and synonym catalog.
        """
        query_lower = query.lower()

        # Direct table synonym match
        for table, meta in self.catalog.items():
            for syn in meta["synonyms"]:
                # Check whole word match
                if re.search(rf"\b{re.escape(syn)}\b", query_lower):
                    return table

        # Column-driven table inference
        for table, col_map in self.column_synonyms.items():
            for col_name, synonyms in col_map.items():
                for syn in synonyms:
                    if re.search(rf"\b{re.escape(syn)}\b", query_lower):
                        return table

        # Default fallback entity
        return "students"

    def extract_columns(self, query: str, table: str) -> List[str]:
        """Resolves projection columns for the target table."""
        query_lower = query.lower()
        matched_columns = []

        if table in self.column_synonyms:
            for col_name, synonyms in self.column_synonyms[table].items():
                for syn in synonyms:
                    if re.search(rf"\b{re.escape(syn)}\b", query_lower):
                        if col_name not in matched_columns:
                            matched_columns.append(col_name)

        # If no specific columns matched, fall back to schema defaults
        if not matched_columns:
            matched_columns = list(self.catalog.get(table, {}).get("default_columns", ["*"]))
        else:
            # If only metric attributes (like cgpa or credits) were matched, ensure primary descriptive column (e.g. name) is also projected
            primary_col_map = {
                "students": "name",
                "courses": "course_name",
                "departments": "dept_name",
                "enrollments": "enrollment_id"
            }
            primary_col = primary_col_map.get(table)
            if primary_col and primary_col not in matched_columns:
                matched_columns.insert(0, primary_col)

        return matched_columns

    def extract_operator_and_value(self, query_snippet: str) -> Optional[Tuple[str, Any]]:
        """Parses relational operator and operand value from text."""
        for pattern, op in OPERATOR_PATTERNS:
            match = re.search(pattern, query_snippet, re.IGNORECASE)
            if match:
                # Text following the operator
                remainder = query_snippet[match.end():].strip()
                # Try finding numeric value first
                num_match = re.search(r"^-?\d+(\.\d+)?", remainder)
                if num_match:
                    val_str = num_match.group(0)
                    val = float(val_str) if "." in val_str else int(val_str)
                    return op, val
                
                # Check for string literal in quotes or next words
                str_match = re.search(r"['\"]([^'\"]+)['\"]", remainder)
                if str_match:
                    return op, str_match.group(1)

                # Fallback for plain string token until end of clause
                tokens = remainder.split()
                if tokens:
                    clean_token = tokens[0].rstrip(",.?!")
                    return op, clean_token
                    
        return None

    def extract_conditions(self, query: str, table: str) -> List[Dict[str, Any]]:
        """Extracts conditional filter predicates from the query."""
        conditions = []
        query_lower = query.lower()

        # Find potential column in condition
        table_cols = self.column_synonyms.get(table, {})
        for col_name, synonyms in table_cols.items():
            for syn in synonyms:
                pattern = rf"\b{re.escape(syn)}\b"
                match = re.search(pattern, query_lower)
                if match:
                    snippet = query_lower[match.start():]
                    parsed = self.extract_operator_and_value(snippet)
                    if parsed:
                        op, val = parsed
                        conditions.append({
                            "column": col_name,
                            "operator": op,
                            "value": val
                        })
                        break

        # If no condition was bound to a specific column, but an operator and number exist
        if not conditions:
            parsed = self.extract_operator_and_value(query_lower)
            if parsed:
                op, val = parsed
                # Infer numeric column based on table
                inferred_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "id")
                conditions.append({
                    "column": inferred_col,
                    "operator": op,
                    "value": val
                })

        return conditions

    def extract_order_and_limit(self, query: str, table: str) -> Tuple[Optional[Dict[str, str]], Optional[int]]:
        """Parses ORDER BY clause and LIMIT."""
        query_lower = query.lower()
        order_by = None
        limit = None

        # Check for "top N" or "bottom N"
        top_match = re.search(r"\btop\s+(\d+)\b", query_lower)
        bottom_match = re.search(r"\bbottom\s+(\d+)\b", query_lower)
        limit_match = re.search(r"\blimit\s+(\d+)\b", query_lower)

        # Default rank column per table
        rank_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "id")

        if top_match:
            limit = int(top_match.group(1))
            order_by = {"column": rank_col, "direction": "DESC"}
        elif bottom_match:
            limit = int(bottom_match.group(1))
            order_by = {"column": rank_col, "direction": "ASC"}
        elif limit_match:
            limit = int(limit_match.group(1))

        # Check explicit sorting keywords
        if "highest" in query_lower or "descending" in query_lower:
            order_by = {"column": rank_col, "direction": "DESC"}
        elif "lowest" in query_lower or "ascending" in query_lower:
            order_by = {"column": rank_col, "direction": "ASC"}

        return order_by, limit

    def extract_aggregation(self, query: str, table: str) -> Optional[Dict[str, str]]:
        """Extracts mathematical aggregation function (AVG, COUNT, MIN, MAX, SUM)."""
        query_lower = query.lower()
        num_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "id")

        if re.search(r"\b(average|avg|mean)\b", query_lower):
            return {"function": "AVG", "column": num_col}
        if re.search(r"\b(count|number of|how many)\b", query_lower):
            return {"function": "COUNT", "column": "*"}
        if re.search(r"\b(maximum|max|highest)\b", query_lower):
            return {"function": "MAX", "column": num_col}
        if re.search(r"\b(minimum|min|lowest)\b", query_lower):
            return {"function": "MIN", "column": num_col}
        if re.search(r"\b(sum|total)\b", query_lower):
            return {"function": "SUM", "column": num_col}

        return None
