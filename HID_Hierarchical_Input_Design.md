# Hierarchical Input Design (HID)
## Project: QueryMind AI — Natural Language to SQL Query Assistant
### Module: Member 1 — NLP Module (Contract Version 1.0 Compliant)

---

## 1. System Module Hierarchy Chart

```
========================================================================================
LEVEL 0: QUERYMIND AI APPLICATION PIPELINE
========================================================================================
   |
   +---> [Member 1] NLP Module (Scope of Ownership)
   |        |
   |        +---> 1.0 Input Handler & Ingestion
   |        |        +--- 1.1 Query Length & Whitespace Validation
   |        |        +--- 1.2 Structured Error Handler (UNSUPPORTED_QUERY)
   |        |
   |        +---> 2.0 Text Preprocessing Submodule (backend/app/nlp/preprocessing.py)
   |        |        +--- 2.1 Lexical Tokenizer & Symbol Normalizer
   |        |        +--- 2.2 Stop-Word Filter with Operator & Keyword Preservation
   |        |        +--- 2.3 Morphological Lemmatizer
   |        |        +--- 2.4 POS Tagger
   |        |
   |        +---> 3.0 Intent Classification Submodule (backend/app/nlp/intent_classifier.py)
   |        |        +--- 3.1 SELECT Intent Classifier
   |        |        +--- 3.2 FILTER Intent Classifier
   |        |        +--- 3.3 AGGREGATE Intent Classifier
   |        |
   |        +---> 4.0 Entity & Clause Extraction Submodule (backend/app/nlp/entity_extractor.py)
   |        |        +--- 4.1 Schema Resolver (students, courses, enrollments)
   |        |        +--- 4.2 Column Projection Resolver
   |        |        +--- 4.3 Condition Predicate Extractor (column, operator, value)
   |        |        +--- 4.4 Join Relation Extractor (students <-> enrollments <-> courses)
   |        |        +--- 4.5 Aggregations Extractor (COUNT, AVG, SUM, MIN, MAX)
   |        |        +--- 4.6 Group By Extractor (department-wise, course-wise)
   |        |        +--- 4.7 Order By & Limit Extractor (ASC / DESC, top N)
   |        |
   |        +---> 5.0 NLP Processor Orchestration (backend/app/nlp/processor.py)
   |        |        +--- 5.1 process_natural_language(query: str) -> dict
   |        |        +--- 5.2 Canonical IR Schema Validation & Serialization
   |        |
   |        +---> 6.0 Member 1 Test Suite (test_nlp_engine.py / backend/tests/test_nlp.py)
   |                 +--- 6.1 Section 9 Mandatory Test Cases (9 Queries + Error Case)
   |
   +---> [Member 2] SQL Engine Module (IR -> Parameterized SQL)
   |
   +---> [Member 3] FastAPI Backend & React Frontend (Pipeline Orchestration)
========================================================================================
```

---

## 2. Submodule Definitions & Responsibilities

1. **`backend.app.nlp.preprocessing`**: Cleans and tokenizes natural language queries while strictly retaining relational keywords (e.g., `greater`, `than`, `above`, `count`, `average`, `department-wise`).
2. **`backend.app.nlp.intent_classifier`**: Normalizes all intents into the contract's 3 canonical values: `SELECT`, `FILTER`, `AGGREGATE`.
3. **`backend.app.nlp.entity_extractor`**: Maps query terms to the exact PostgreSQL schema identifiers (`students`, `courses`, `enrollments`) and builds structured arrays for `conditions`, `joins`, `aggregations`, `group_by`, and `order_by`.
4. **`backend.app.nlp.processor`**: Exposes the required single public entry point `process_natural_language(query: str) -> dict` and handles errors according to the Team Integration Contract.
