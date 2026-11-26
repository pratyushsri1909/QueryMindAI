"""
Entity Extractor for QueryMind AI (Member 1 - NLP Module).
Extracts tables, columns, conditions, joins, aggregations, group_by, order_by, and limits
based on PostgreSQL schema defined in Team Integration Contract Version 1.0.
Integrates with lemmatization and preprocessed token metadata.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .schema import DATABASE_SCHEMA, COLUMN_SYNONYMS, SCHEMA_RELATIONSHIPS, OPERATOR_PATTERNS


class EntityExtractor:
    """Extracts schema entities, operators, filters, and structural clauses using preprocessed lemmas."""

    def __init__(self):
        self.schema = DATABASE_SCHEMA
        self.column_synonyms = COLUMN_SYNONYMS
        self.relationships = SCHEMA_RELATIONSHIPS

    def extract_table(self, query: str, prep: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Identifies the primary table using lemmatized tokens and synonyms.
        Returns None if no database entity or recognizable domain attribute is found.
        """
        query_lower = query.lower()
        lemmas = set(prep.get("lemmas", [])) if prep else set()
        lemmatized_query = prep.get("lemmatized_query", query_lower) if prep else query_lower

        # 1. Match explicit table synonyms against lemmatized query & lemma set
        for table, meta in self.schema.items():
            for syn in meta["synonyms"]:
                if syn in lemmas or re.search(rf"\b{re.escape(syn)}\b", lemmatized_query) or re.search(rf"\b{re.escape(syn)}\b", query_lower):
                    return table

        # 2. Check column-based table inference
        for table, col_map in self.column_synonyms.items():
            for col_name, synonyms in col_map.items():
                for syn in synonyms:
                    if syn in lemmas or re.search(rf"\b{re.escape(syn)}\b", lemmatized_query) or re.search(rf"\b{re.escape(syn)}\b", query_lower):
                        return table

        # If query has generic keywords like 'all', 'records', 'details' without domain entity
        # check if it's completely out of domain
        return None

    def extract_columns(self, query: str, table: str, prep: Optional[Dict[str, Any]] = None) -> List[str]:
        """Identifies projected columns for the target table, leveraging lemmatized inputs."""
        query_lower = query.lower()
        lemmas = set(prep.get("lemmas", [])) if prep else set()
        lemmatized_query = prep.get("lemmatized_query", query_lower) if prep else query_lower

        matched_columns = []

        if table in self.column_synonyms:
            for col_name, synonyms in self.column_synonyms[table].items():
                for syn in synonyms:
                    if syn in lemmas or re.search(rf"\b{re.escape(syn)}\b", lemmatized_query) or re.search(rf"\b{re.escape(syn)}\b", query_lower):
                        if col_name not in matched_columns:
                            matched_columns.append(col_name)

        # Multi-table projections: if students enrolled in courses, include course name
        if table == "students" and ("course" in lemmas or "course" in lemmatized_query or "enrolled" in query_lower):
            if "name" not in matched_columns:
                matched_columns.append("name")
            if "course_name" not in matched_columns:
                matched_columns.append("course_name")
            return matched_columns

        if not matched_columns:
            if table == "students":
                matched_columns = ["name", "cgpa"]
            elif table == "courses":
                matched_columns = ["course_name", "credits"]
            else:
                matched_columns = list(self.schema.get(table, {}).get("default_columns", []))
        else:
            primary_col = "name" if table == "students" else ("course_name" if table == "courses" else None)
            if primary_col and primary_col not in matched_columns:
                matched_columns.insert(0, primary_col)

        return matched_columns

    def extract_conditions(self, query: str, table: str, prep: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extracts single or multiple conditional WHERE filtering clauses.
        Supports compound conditions joined by 'and' or commas.
        """
        conditions = []
        query_lower = query.lower()
        lemmatized_query = prep.get("lemmatized_query", query_lower) if prep else query_lower

        # 1. Department condition check: e.g. "from CSE department", "department is CSE", "department CSE"
        dept_match = (
            re.search(r"\b(?:from|in)\s+([A-Za-z0-9]+)\s+(?:department|dept|branch)\b", query_lower) or
            re.search(r"\b(?:department|dept|branch)\s*(?:is|=|:)?\s*([A-Za-z0-9]+)\b", query_lower)
        )
        if dept_match:
            dept_val = dept_match.group(1).upper()
            if dept_val not in {"THE", "ALL", "EACH", "EVERY", "THIS", "DESCENDING", "ASCENDING", "ORDER", "WISE"}:
                conditions.append({
                    "column": "department",
                    "operator": "=",
                    "value": dept_val
                })

        # 2. Split compound query into clauses on conjunctions ('and', ';') to extract multiple conditions
        clauses = re.split(r"\band\b|;", query_lower)
        if not clauses:
            clauses = [query_lower]

        for clause in clauses:
            clause_str = clause.strip()
            for pattern, op in OPERATOR_PATTERNS:
                match = re.search(pattern, clause_str)
                if match:
                    remainder = clause_str[match.end():].strip()
                    num_match = re.search(r"^-?\d+(\.\d+)?", remainder)
                    if num_match:
                        val_str = num_match.group(0)
                        val = float(val_str) if "." in val_str else int(val_str)

                        # Determine target column from preceding text in this clause or query
                        prefix = clause_str[:match.start()]
                        target_col = None

                        if table in self.column_synonyms:
                            for col_name, synonyms in self.column_synonyms[table].items():
                                for syn in synonyms:
                                    if syn in prefix or syn in clause_str:
                                        target_col = col_name
                                        break
                                if target_col:
                                    break

                        # Fallback default column
                        if not target_col:
                            target_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "student_id")

                        # Avoid duplicate entries
                        if not any(c["column"] == target_col and c["value"] == val for c in conditions):
                            conditions.append({
                                "column": target_col,
                                "operator": op,
                                "value": val
                            })
                        break

        # Fallback single scan if clause splitting did not catch operator
        if not conditions:
            for pattern, op in OPERATOR_PATTERNS:
                match = re.search(pattern, query_lower)
                if match:
                    remainder = query_lower[match.end():].strip()
                    num_match = re.search(r"^-?\d+(\.\d+)?", remainder)
                    if num_match:
                        val_str = num_match.group(0)
                        val = float(val_str) if "." in val_str else int(val_str)
                        target_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "student_id")
                        conditions.append({
                            "column": target_col,
                            "operator": op,
                            "value": val
                        })
                        break

        return conditions

    def extract_aggregations(self, query: str, table: str, prep: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Extracts aggregate functions (COUNT, AVG, SUM, MIN, MAX)."""
        query_lower = query.lower()
        lemmas = set(prep.get("lemmas", [])) if prep else set()
        aggregations = []

        # COUNT
        if "count" in lemmas or re.search(r"\b(count|how many|number of|total count)\b", query_lower):
            aggregations.append({
                "function": "COUNT",
                "column": "*",
                "alias": "total_count"
            })

        # AVG (only on numeric metrics; avoid applying AVG to VARCHAR grade)
        if "average" in lemmas or re.search(r"\b(average|avg|mean)\b", query_lower):
            if table in {"students", "courses"}:
                col = "cgpa" if table == "students" else "credits"
                aggregations.append({
                    "function": "AVG",
                    "column": col,
                    "alias": f"average_{col}"
                })

        # SUM (only on numeric metrics)
        if "sum" in lemmas or (re.search(r"\b(sum|total credits)\b", query_lower) and not re.search(r"\btotal count\b", query_lower)):
            if table in {"students", "courses"}:
                col = "credits" if table == "courses" else "cgpa"
                aggregations.append({
                    "function": "SUM",
                    "column": col,
                    "alias": f"total_{col}"
                })

        # MAX
        if "maximum" in lemmas or re.search(r"\b(maximum|max|highest marks)\b", query_lower):
            col = "cgpa" if table == "students" else ("credits" if table == "courses" else "grade")
            aggregations.append({
                "function": "MAX",
                "column": col,
                "alias": f"max_{col}"
            })

        # MIN
        if "minimum" in lemmas or re.search(r"\b(minimum|min|lowest marks)\b", query_lower):
            col = "cgpa" if table == "students" else ("credits" if table == "courses" else "grade")
            aggregations.append({
                "function": "MIN",
                "column": col,
                "alias": f"min_{col}"
            })

        return aggregations

    def extract_group_by(self, query: str, table: str, prep: Optional[Dict[str, Any]] = None) -> List[str]:
        """Extracts GROUP BY columns."""
        query_lower = query.lower()
        group_by = []

        if re.search(r"\bdepartment[\s-]wise\b|\bby department\b|\bper department\b", query_lower):
            group_by.append("department")
        elif re.search(r"\bcourse[\s-]wise\b|\bby course\b|\bper course\b", query_lower):
            group_by.append("course_id")
        elif re.search(r"\bbatch[\s-]wise\b|\bby batch\b", query_lower):
            group_by.append("batch")

        return group_by

    def extract_order_by(self, query: str, table: str, prep: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Extracts ORDER BY instructions array."""
        query_lower = query.lower()
        lemmas = set(prep.get("lemmas", [])) if prep else set()
        order_by = []
        default_sort_col = "cgpa" if table == "students" else ("credits" if table == "courses" else "student_id")
        sort_col = default_sort_col

        order_clause_match = re.search(r"\b(?:ordered|order|sorted|sort)\s+by\s+(.+)$", query_lower)
        if order_clause_match and table in self.column_synonyms:
            clause_tail = order_clause_match.group(1)
            for col_name, synonyms in self.column_synonyms[table].items():
                if any(re.search(rf"\b{re.escape(syn)}\b", clause_tail) for syn in synonyms):
                    sort_col = col_name
                    break

        if (
            "ascending" in lemmas
            or re.search(r"\b(ascending|asc)\b", query_lower)
            or re.search(r"\bbottom\s+\d+\b|\b(?:bottom|lowest|worst)\b", query_lower)
        ):
            order_by.append({
                "column": sort_col,
                "direction": "ASC"
            })
        elif (
            "descending" in lemmas
            or re.search(r"\b(descending|desc)\b", query_lower)
            or re.search(r"\btop\s+\d+\b|\b(?:top|highest|best)\b", query_lower)
        ):
            order_by.append({
                "column": sort_col,
                "direction": "DESC"
            })
        elif order_clause_match:
            order_by.append({
                "column": sort_col,
                "direction": "ASC"
            })

        return order_by

    def extract_limit(self, query: str, prep: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Extracts LIMIT integer."""
        query_lower = query.lower()
        top_match = re.search(r"\b(?:top|first|limit)\s+(\d+)\b", query_lower)
        if top_match:
            return int(top_match.group(1))
        bottom_match = re.search(r"\bbottom\s+(\d+)\b", query_lower)
        if bottom_match:
            return int(bottom_match.group(1))
        return None

    def extract_joins(self, query: str, primary_table: str, prep: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Identifies required table joins.
        For queries connecting students with courses (e.g. 'Show students enrolled in each course'),
        extracts both:
        1. enrollments (students.student_id = enrollments.student_id)
        2. courses (enrollments.course_id = courses.course_id)
        """
        query_lower = query.lower()
        lemmas = set(prep.get("lemmas", [])) if prep else set()
        lemmatized_query = prep.get("lemmatized_query", query_lower) if prep else query_lower
        joins = []

        is_student_query = primary_table == "students"
        is_course_query = primary_table == "courses"

        has_course_mention = "course" in lemmas or "course" in lemmatized_query or "course" in query_lower or "class" in lemmas or "subject" in lemmas
        has_student_mention = "student" in lemmas or "student" in lemmatized_query or "pupil" in lemmas
        has_enroll_mention = "enroll" in lemmas or "enrollment" in lemmas or "enrolled" in query_lower or "registration" in lemmas

        # Case 1: Primary table is students and courses are mentioned (e.g. 'Show students enrolled in each course')
        if is_student_query and (has_course_mention or has_enroll_mention):
            # First hop: students -> enrollments
            joins.append({
                "table": "enrollments",
                "type": "INNER",
                "left_column": "students.student_id",
                "right_column": "enrollments.student_id"
            })

            # Second hop: enrollments -> courses (when course information is needed)
            if has_course_mention:
                joins.append({
                    "table": "courses",
                    "type": "INNER",
                    "left_column": "enrollments.course_id",
                    "right_column": "courses.course_id"
                })

        # Case 2: Primary table is courses and students are mentioned (e.g. 'Show courses with enrolled students')
        elif is_course_query and (has_student_mention or has_enroll_mention):
            # First hop: courses -> enrollments
            joins.append({
                "table": "enrollments",
                "type": "INNER",
                "left_column": "courses.course_id",
                "right_column": "enrollments.course_id"
            })

            # Second hop: enrollments -> students
            if has_student_mention:
                joins.append({
                    "table": "students",
                    "type": "INNER",
                    "left_column": "enrollments.student_id",
                    "right_column": "students.student_id"
                })

        return joins
