"""
NLP Module for QueryMind AI (Member 1).
Exposes the required public contract function: process_natural_language
"""

from .processor import process_natural_language, NLPProcessor
from .preprocessing import TextPreprocessor
from .intent_classifier import IntentClassifier
from .entity_extractor import EntityExtractor
from .schema import DATABASE_SCHEMA, COLUMN_SYNONYMS

__all__ = [
    "process_natural_language",
    "NLPProcessor",
    "TextPreprocessor",
    "IntentClassifier",
    "EntityExtractor",
    "DATABASE_SCHEMA",
    "COLUMN_SYNONYMS"
]
