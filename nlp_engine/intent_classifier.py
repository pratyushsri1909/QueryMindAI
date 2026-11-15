"""
Intent Classifier for QueryMind AI (Member 1 - NLP Engine).
Classifies the primary intent of natural language queries into:
- RETRIEVAL
- FILTER
- COUNT
- AGGREGATION
- SORT
"""

import re
from typing import Dict, Any, Tuple


class IntentClassifier:
    """Classifies user queries into standard SQL-oriented semantic intents."""

    def __init__(self):
        # Intent patterns sorted by evaluation priority
        self.count_patterns = [
            r"\bhow many\b", r"\bcount\b", r"\bnumber of\b", r"\btotal count\b"
        ]
        self.aggregation_patterns = [
            r"\baverage\b", r"\bavg\b", r"\bmean\b", r"\bsum of\b", r"\btotal\b",
            r"\bminimum\b", r"\bmin\b", r"\bmaximum\b", r"\bmax\b",
            r"\bhighest marks\b", r"\blowest marks\b"
        ]
        self.sort_patterns = [
            r"\btop\s+\d+\b", r"\bbottom\s+\d+\b", r"\bsort by\b", r"\border by\b",
            r"\brank\b", r"\bascending\b", r"\bdescending\b", r"\bhighest\b", r"\blowest\b"
        ]
        self.filter_patterns = [
            r"\bgreater than\b", r"\bless than\b", r"\babove\b", r"\bbelow\b",
            r"\bhaving\b", r"\bwhere\b", r"\bequal to\b", r"\bexceeding\b",
            r"\bat least\b", r"\bat most\b", r">=", r"<=", r"!=", r">", r"<", r"="
        ]

    def classify(self, query: str, preprocessed_data: Dict[str, Any]) -> Tuple[str, float]:
        """
        Determines the intent and confidence score.
        Returns: (intent_name, confidence)
        """
        query_lower = query.lower()
        cleaned_query = preprocessed_data.get("cleaned_query", query_lower).lower()

        # 1. Check COUNT intent
        for pat in self.count_patterns:
            if re.search(pat, cleaned_query):
                return "COUNT", 0.95

        # 2. Check AGGREGATION intent
        for pat in self.aggregation_patterns:
            if re.search(pat, cleaned_query):
                return "AGGREGATION", 0.92

        # 3. Check SORT intent
        for pat in self.sort_patterns:
            if re.search(pat, cleaned_query):
                return "SORT", 0.90

        # 4. Check FILTER intent
        for pat in self.filter_patterns:
            if re.search(pat, cleaned_query):
                return "FILTER", 0.94

        # 5. Default to RETRIEVAL
        return "RETRIEVAL", 0.85
