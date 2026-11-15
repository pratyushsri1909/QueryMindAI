# Hierarchical Input Design (HID)
## Project: QueryMind AI — Natural Language to SQL Query Assistant
### Module: Member 1 — NLP Engine & Natural Language Understanding

---

## 1. Overview
The **Hierarchical Input Design (HID)** presents the hierarchical decomposition of the Member 1 (NLP Engine) architecture. It organizes the system into functional layers, parent modules, child submodules, and leaf components responsible for turning unstructured natural language inputs into the validated Intermediate Representation (IR) JSON.

---

## 2. System Module Hierarchy Chart

```
========================================================================================
LEVEL 0: QUERYMIND AI SYSTEM (End-to-End System)
========================================================================================
   |
   +---> [Member 1] NLP Engine Module (Core Natural Language Understanding) <--- (OUR SCOPE)
   |        |
   |        +---> 1.0 Input Ingestion & Sanitization Layer
   |        |        +--- 1.1 Query Ingestion Handler
   |        |        +--- 1.2 Boundary & Length Validator
   |        |        +--- 1.3 Text Sanitizer & Normalizer
   |        |
   |        +---> 2.0 Text Preprocessing Submodule
   |        |        +--- 2.1 Lexical Tokenizer (Word & Punctuation Boundary Splitting)
   |        |        +--- 2.2 Case Normalizer (Lowercasing & Accent Folding)
   |        |        +--- 2.3 Stop-Word Filtering & Keyword Preservation
   |        |        +--- 2.4 Morphological Lemmatizer (Root Word Reducer)
   |        |        +--- 2.5 Part-of-Speech (POS) Tagger & Syntactic Dependency Parser
   |        |
   |        +---> 3.0 Intent Classification Submodule
   |        |        +--- 3.1 Pattern & Keyword Matcher (Rule-based heuristics)
   |        |        +--- 3.2 Semantic Similarity & Intent Scorer
   |        |        +--- 3.3 Intent Classifier Engine:
   |        |                 * RETRIEVAL Intent Handler
   |        |                 * FILTER Intent Handler
   |        |                 * COUNT Intent Handler
   |        |                 * AGGREGATION Intent Handler
   |        |                 * SORT Intent Handler
   |        |
   |        +---> 4.0 Entity & Slot Extraction Submodule
   |        |        +--- 4.1 Schema Resolver & Knowledge Base
   |        |                 * Table Entity Matcher (with synonym aliases)
   |        |                 * Column Attribute Matcher (with semantic aliases)
   |        |        +--- 4.2 Condition & Predicate Extractor
   |        |                 * Relational Operator Parser (>, <, =, !=, >=, <=, LIKE)
   |        |                 * Numeric Literal & Range Extractor (Integers, Floats)
   |        |                 * String & Categorical Literal Extractor
   |        |        +--- 4.3 Aggregation & Function Extractor (AVG, SUM, MIN, MAX, COUNT)
   |        |        +--- 4.4 Order & Limit Extractor
   |        |                 * Sort Direction Resolver (ASC vs DESC)
   |        |                 * Top-N / Limit Quantifier Parser
   |        |
   |        +---> 5.0 Intermediate Representation (IR) Builder & Validator
   |        |        +--- 5.1 IR Data Structure Assembler
   |        |        +--- 5.2 JSON Schema Compliance Validator
   |        |        +--- 5.3 Ambiguity Detection & Confidence Estimator
   |        |        +--- 5.4 Fallback & Paraphrase Handler
   |        |
   |        +---> 6.0 Integration & Test Suite Submodule
   |                 +--- 6.1 NLP Unit Test Harness
   |                 +--- 6.2 Golden Benchmark Query Suite (50-100 Test Cases)
   |                 +--- 6.3 Metric Evaluator (Intent Accuracy, Slot Precision/Recall)
   |
   +---> [Member 2] Database & SQL Engine Module (PostgreSQL & SQLGlot)
   |
   +---> [Member 3] Backend, Frontend & Integration Module (FastAPI & React)
========================================================================================
```

---

## 3. Detailed Submodule Breakdown

### Module 1.0: Input Ingestion & Sanitization Layer
* **1.1 Query Ingestion Handler**: Receives the raw query string from the API interface.
* **1.2 Boundary & Length Validator**: Ensures queries are within character boundaries (3 - 500 characters) and rejects malicious control characters.
* **1.3 Text Sanitizer & Normalizer**: Unifies diverse quote symbols (`'`, `"`, `“`, `”`), normalizes operator notations (e.g. converting `greater than or equal to` into `>=`), and cleans excess whitespaces.

### Module 2.0: Text Preprocessing Submodule
* **2.1 Lexical Tokenizer**: Splits the clean query string into discrete tokens (words, numbers, symbols).
* **2.2 Case Normalizer**: Maps tokens to standard lowercase for casing-insensitive schema matching.
* **2.3 Stop-Word Filtering**: Removes conversational filler words (`"please"`, `"show me"`, `"can you"`) while strictly **retaining** syntactically significant keywords (`"than"`, `"above"`, `"not"`, `"top"`, `"all"`).
* **2.4 Lemmatizer**: Reduces plural/inflected nouns and verbs to canonical lemma forms (`"departments"` -> `"department"`, `"calculated"` -> `"calculate"`).
* **2.5 POS Tagger**: Assigns grammatical categories (Noun, Verb, Adjective, Comparative, Numeral) to aid entity vs. predicate disambiguation.

### Module 3.0: Intent Classification Submodule
* **3.1 Pattern & Keyword Matcher**: Scans token sequences for intent markers.
* **3.2 Semantic Similarity & Intent Scorer**: Computes confidence scores for candidate intents.
* **3.3 Intent Classifier Engine**: Resolves the final primary user intent:
  - `RETRIEVAL`: Direct select queries without specific conditional filters.
  - `FILTER`: Queries demanding conditional predicates (`cgpa > 8.5`).
  - `COUNT`: Queries requesting counts of items or rows (`how many students...`).
  - `AGGREGATION`: Mathematical reductions (`average cgpa`, `highest marks`).
  - `SORT`: Queries requesting ranked or ordered lists (`top 5 students`).

### Module 4.0: Entity & Slot Extraction Submodule
* **4.1 Schema Resolver & Knowledge Base**:
  - Matches tokens against approved tables (`students`, `courses`, `departments`, `enrollments`).
  - Resolves colloquial synonyms (`"gpa"` -> `"cgpa"`, `"stream"` -> `"department_id"`).
  - Selects projection columns (`["name", "cgpa"]`).
* **4.2 Condition & Predicate Extractor**:
  - Identifies comparison verbs/words and maps them to standard SQL operators:
    - `"greater than"`, `"above"`, `"more than"`, `">"` -> `>`
    - `"less than"`, `"below"`, `"under"`, `"<"` -> `<`
    - `"equal to"`, `"is"`, `"having"` -> `=`
  - Extracts operand values (e.g. float `8.5`, department name `'Computer Science'`).
* **4.3 Aggregation & Function Extractor**:
  - Detects functions: `AVG`, `SUM`, `MIN`, `MAX`, `COUNT` and binds them to relevant numeric columns.
* **4.4 Order & Limit Extractor**:
  - Detects keywords like `"top"`, `"highest"`, `"best"` -> `DESC` order with specified limit.
  - Detects keywords like `"bottom"`, `"lowest"`, `"worst"` -> `ASC` order.

### Module 5.0: Intermediate Representation (IR) Builder & Validator
* **5.1 IR Data Structure Assembler**: Organizes all parsed slots into the canonical JSON dictionary.
* **5.2 JSON Schema Compliance Validator**: Validates the assembled dictionary against the shared integration contract agreed upon by Member 2 and Member 3.
* **5.3 Ambiguity Detection & Confidence Estimator**: Calculates confidence score; flags low-confidence or ambiguous queries.
* **5.4 Fallback & Paraphrase Handler**: Applies heuristic defaults if certain non-critical slots are omitted.

### Module 6.0: Integration & Test Suite Submodule
* **6.1 Unit Test Harness**: Automated tests executing test cases against each subcomponent.
* **6.2 Golden Benchmark Query Suite**: Curated 50+ benchmark natural language queries covering single-table, multi-condition, aggregate, and edge cases.
* **6.3 Metric Evaluator**: Calculates classification accuracy, slot precision, recall, and end-to-end IR validity.

---

## 4. Hierarchical Data Flow Model

```
[Raw User Query]
       │
       ▼
[1.0 Ingestion & Sanitization] ───► Sanitized Query String
       │
       ▼
[2.0 Text Preprocessing] ────────► Preprocessed Tokens & POS Tags
       │
       ├──────────────────────────────────┬──────────────────────────────────┐
       ▼                                  ▼                                  ▼
[3.0 Intent Classifier]        [4.1 Schema Resolver]             [4.2-4.4 Slot Extractor]
 (Intent: FILTER/COUNT/...)     (Table: students, Cols: name,cgpa) (Operator: >, Value: 8.5)
       │                                  │                                  │
       └──────────────────────────────────┼──────────────────────────────────┘
                                          │
                                          ▼
                      [5.0 IR Builder & Validator]
                                          │
                                          ▼
                      [Standardized Output: IR JSON]
                                          │
                     (Handoff to Member 2: SQL Engine)
```
