"""
Unified Root Wrapper for NLP Engine (Member 1).
Maintains backwards-compatibility with both nlp_engine and backend.app.nlp.
"""

from backend.app.nlp.processor import process_natural_language, NLPProcessor
from backend.app.nlp.preprocessing import TextPreprocessor
from backend.app.nlp.intent_classifier import IntentClassifier
from backend.app.nlp.entity_extractor import EntityExtractor
from backend.app.nlp.schema import DATABASE_SCHEMA, COLUMN_SYNONYMS

# Alias for root-level import convenience
NLPEngine = NLPProcessor

__all__ = [
    "process_natural_language",
    "NLPEngine",
    "NLPProcessor",
    "TextPreprocessor",
    "IntentClassifier",
    "EntityExtractor",
    "DATABASE_SCHEMA",
    "COLUMN_SYNONYMS"
]
