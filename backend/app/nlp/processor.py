"""
NLP Processor for QueryMind AI (Member 1 - NLP Module).
Implements the core public interface required by Team Integration Contract Version 1.0:
    process_natural_language(query: str) -> dict
"""

import re
from typing import Dict, Any
from .preprocessing import TextPreprocessor
from .intent_classifier import IntentClassifier
from .entity_extractor import EntityExtractor


class NLPProcessor:
    """Orchestrates natural language processing pipeline to construct Canonical IR."""

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()

    def process(self, query: str) -> Dict[str, Any]:
        """Processes query string and outputs Canonical IR or structured error."""
        if not query or not query.strip():
            return {
                "success": False,
                "error": {
                    "code": "UNSUPPORTED_QUERY",
                    "message": "Input query cannot be empty or whitespace."
                }
            }

        cleaned = self.preprocessor.clean_text(query)
        if len(cleaned) < 3:
            return {
                "success": False,
                "error": {
                    "code": "UNSUPPORTED_QUERY",
                    "message": "Query is too short to extract meaningful intent."
                }
            }

        try:
            # 1. Schema entity & slot extraction
            table = self.entity_extractor.extract_table(cleaned)
            columns = self.entity_extractor.extract_columns(cleaned, table)
            conditions = self.entity_extractor.extract_conditions(cleaned, table)
            joins = self.entity_extractor.extract_joins(cleaned, table)
            aggregations = self.entity_extractor.extract_aggregations(cleaned, table)
            group_by = self.entity_extractor.extract_group_by(cleaned, table)
            order_by = self.entity_extractor.extract_order_by(cleaned, table)
            limit = self.entity_extractor.extract_limit(cleaned)

            # 2. Intent classification
            intent = self.intent_classifier.classify(
                query=cleaned,
                has_conditions=bool(conditions),
                has_aggregations=bool(aggregations)
            )

            # 3. Assemble Canonical Intermediate Representation (Contract Section 2)
            ir = {
                "intent": intent,
                "table": table,
                "columns": columns,
                "conditions": conditions,
                "joins": joins,
                "aggregations": aggregations,
                "group_by": group_by,
                "order_by": order_by,
                "limit": limit
            }

            return ir

        except Exception as exc:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_IR",
                    "message": f"Failed to generate IR: {str(exc)}"
                }
            }


# Singleton instance for public function access
_processor_instance = NLPProcessor()


def process_natural_language(query: str) -> dict:
    """
    Public entrypoint function required by Member 1 contract:
    Converts a natural language query into the Canonical Intermediate Representation (IR).

    Args:
        query (str): The plain English input query from user.

    Returns:
        dict: The Canonical IR dictionary matching Version 1.0 of the contract,
              or a structured error dictionary on failure.
    """
    return _processor_instance.process(query)
