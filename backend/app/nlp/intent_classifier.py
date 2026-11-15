"""
Intent Classifier for QueryMind AI (Member 1 - NLP Module).
Strictly adheres to Contract 1.0 Intent specifications:
- SELECT
- FILTER
- AGGREGATE
"""

import re
from typing import Dict, Any


class IntentClassifier:
    """Classifies queries into canonical contract intents: SELECT, FILTER, AGGREGATE."""

    def __init__(self):
        self.aggregate_patterns = [
            r"\bcount\b", r"\bhow many\b", r"\bnumber of\b", r"\btotal count\b",
            r"\baverage\b", r"\bavg\b", r"\bmean\b", r"\bsum\b", r"\btotal\b",
            r"\bminimum\b", r"\bmin\b", r"\bmaximum\b", r"\bmax\b"
        ]
        self.filter_patterns = [
            r"\bgreater than\b", r"\babove\b", r"\bless than\b", r"\bbelow\b",
            r"\bhaving\b", r"\bwhere\b", r"\bequal to\b", r"\bexceeding\b",
            r"\bat least\b", r"\bat most\b", r"\bfrom\s+[A-Za-z]+\s+department\b",
            r"\bin\s+[A-Za-z]+\s+department\b", r">=", r"<=", r"!=", r">", r"<", r"="
        ]

    def classify(self, query: str, has_conditions: bool = False, has_aggregations: bool = False) -> str:
        """
        Returns one of: 'SELECT', 'FILTER', 'AGGREGATE'.
        """
        query_lower = query.lower()

        # 1. AGGREGATE intent (Count, Average, Sum, Min, Max)
        if has_aggregations or any(re.search(pat, query_lower) for pat in self.aggregate_patterns):
            return "AGGREGATE"

        # 2. FILTER intent (conditions present)
        if has_conditions or any(re.search(pat, query_lower) for pat in self.filter_patterns):
            return "FILTER"

        # 3. SELECT intent (default retrieval, sorting, limits, or plain joins)
        return "SELECT"
