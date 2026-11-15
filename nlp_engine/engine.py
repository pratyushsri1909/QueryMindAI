"""
NLP Engine Main Orchestrator for QueryMind AI (Member 1 - NLP Engine).
Coordinates preprocessing, classification, extraction, and IR generation.
"""

from typing import Dict, Any, Optional
from .preprocessor import Preprocessor
from .intent_classifier import IntentClassifier
from .entity_extractor import EntityExtractor
from .ir_builder import IRBuilder, IRValidationError


class NLPEngine:
    """
    Independent NLP Module for QueryMind AI.
    Converts unstructured English natural language queries into
    deterministic, validated Intermediate Representation (IR) JSON.
    """

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.ir_builder = IRBuilder()

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Executes the full pipeline:
        1. Ingestion & Preprocessing
        2. Intent Classification
        3. Entity & Slot Extraction (Table, Columns, Conditions, Limits, Aggregates)
        4. IR JSON Construction & Validation
        """
        if not query or not query.strip():
            raise ValueError("Input query cannot be empty.")

        # Stage 1: Preprocessing
        prep = self.preprocessor.preprocess(query)

        # Stage 2: Intent Classification
        intent, intent_confidence = self.intent_classifier.classify(query, prep)

        # Stage 3: Entity & Slot Extraction
        table = self.entity_extractor.extract_table(query, prep["lemmas"])
        columns = self.entity_extractor.extract_columns(query, table)
        conditions = self.entity_extractor.extract_conditions(query, table)
        order_by, limit = self.entity_extractor.extract_order_and_limit(query, table)
        aggregation = self.entity_extractor.extract_aggregation(query, table)

        # Re-align intent if conditions exist and intent was default RETRIEVAL
        if conditions and intent == "RETRIEVAL":
            intent = "FILTER"

        # Calculate overall confidence score
        overall_confidence = intent_confidence
        if not conditions and intent == "FILTER":
            overall_confidence -= 0.15

        # Stage 4: IR JSON Assembly & Validation
        ir = self.ir_builder.build_ir(
            intent=intent,
            table=table,
            columns=columns,
            conditions=conditions,
            order_by=order_by,
            limit=limit,
            aggregation=aggregation,
            confidence_score=max(0.5, min(1.0, overall_confidence))
        )

        return ir
