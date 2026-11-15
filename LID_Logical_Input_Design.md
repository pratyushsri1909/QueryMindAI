# Logical Input Design (LID)
## Project: QueryMind AI — Natural Language to SQL Query Assistant
### Module: Member 1 — NLP Engine & Natural Language Understanding

---

## 1. Overview & Purpose
The **Logical Input Design (LID)** specifies the logical characteristics, structural definitions, validation constraints, and lexical representations of all inputs received and processed by the **Member 1 (NLP Engine)** module.

The primary role of the NLP Engine is to ingest unstructured or semi-structured natural language user prompts and transform them into a deterministic, validated **Intermediate Representation (IR)** JSON structure that Member 2 (SQL Engine) and Member 3 (FastAPI & UI) consume.

---

## 2. Input Specifications

### 2.1 Primary Input: Natural Language Query (NLQ)
- **Field Name**: `query_text`
- **Data Type**: `String (UTF-8)`
- **Origin**: End user via Web UI (React) -> FastAPI Orchestrator (Member 3) -> NLP Engine (Member 1).
- **Logical Format**: Free-form English text sentences or phrases.
- **Constraints**:
  - Minimum Length: 3 characters (e.g., `"all students"`).
  - Maximum Length: 500 characters.
  - Allowed Characters: Alphanumeric (`a-z`, `A-Z`, `0-9`), standard punctuation (`.`, `,`, `?`, `'`, `"`, `>`, `<`, `=`, `!`), and whitespace.
  - Rejection / Sanitization: Null bytes, binary data, script injections (`<script>`), non-printable ASCII control characters.

### 2.2 Secondary / Contextual Input: Schema Catalog
- **Field Name**: `schema_context`
- **Data Type**: `Object (Dictionary)`
- **Logical Structure**:
  - `tables`: List of database entities (`students`, `courses`, `departments`, `enrollments`).
  - `columns`: Entity attributes mapping (e.g., `students -> [id, name, cgpa, email, department_id, admission_year]`).
  - `aliases_and_synonyms`: Domain-specific synonyms (e.g., `"marks"` -> `cgpa`, `"gpa"` -> `cgpa`, `"branch"` -> `department_id`, `"pupil"` -> `students`).

---

## 3. Logical Input Preprocessing Structure

Before semantic interpretation, the raw input undergoes logical normalization:

| Stage | Input State | Logical Transformation | Output State |
| :--- | :--- | :--- | :--- |
| **Case Normalization** | Mixed case (e.g., `"Show All Students"`) | Case-folding to lowercase | `"show all students"` |
| **Punctuation Clean** | Punctuation with noise (`"cgpa >= 8.5?!"`) | Normalizes comparison symbols (`>=`, `<=`, `!=`, `<>`) and strips trailing punctuation | Normalized string tokens |
| **Tokenization** | Raw string stream | Whitespace & delimiter segmentation | List of lexical tokens `[Token]` |
| **Stop-word Filter** | Filler words (`"please", "can", "you"`) | Removal of non-semantic conversational tokens while preserving query-critical operators (`"greater"`, `"than"`, `"top"`, `"count"`) | Filtered semantic tokens |
| **Lemmatization & Stemming** | Inflected forms (`"enrolled"`, `"highest"`, `"courses"`) | Lemmatization to base dictionary form (`"enroll"`, `"high"`, `"course"`) | Canonical lemma tokens |

---

## 4. Input Lexicon & Domain Slot Mappings

### 4.1 Intent Vocabulary Mapping
The NLP engine logically maps input phrases to one of the canonical system intents:

| Logical Intent | Target Meaning | Input Keyword Indicators |
| :--- | :--- | :--- |
| `RETRIEVAL` | Fetch records without specific conditional filtering | `"show"`, `"display"`, `"list"`, `"get"`, `"fetch"`, `"find all"` |
| `FILTER` | Conditional filtering of rows based on predicate logic | `"where"`, `"having"`, `"whose"`, `"greater than"`, `"less than"`, `"equal to"`, `"after"`, `"before"` |
| `COUNT` | Cardinality quantification | `"how many"`, `"count"`, `"number of"`, `"total count"` |
| `AGGREGATION` | Mathematical aggregation functions | `"average"`, `"avg"`, `"mean"`, `"minimum"`, `"min"`, `"lowest"`, `"maximum"`, `"max"`, `"highest"`, `"sum"`, `"total"` |
| `SORT` | Ordering / ranking of data rows | `"sort by"`, `"ordered by"`, `"rank"`, `"top"`, `"bottom"`, `"ascending"`, `"descending"` |

### 4.2 Entity / Slot Logical Schema
Input queries are parsed into structured entity slots:

1. **Target Entity (Table)**:
   - Logical Type: `Enum {students, courses, departments, enrollments}`
   - Synonyms:
     - `students`: `student`, `pupils`, `candidates`, `scholars`
     - `courses`: `course`, `subjects`, `classes`, `modules`
     - `departments`: `department`, `dept`, `branch`, `stream`
     - `enrollments`: `enrollment`, `registrations`, `grades`

2. **Attribute Slots (Columns)**:
   - Logical Type: `List of Valid Schema Columns` (e.g., `["name", "cgpa"]`)
   - Default: All primary columns or wildcard `*` if unspecified.

3. **Predicate Condition Slots**:
   - `column`: Target attribute name (e.g., `"cgpa"`).
   - `operator`: Logical relational operator `Enum {>, <, >=, <=, =, !=, LIKE, BETWEEN}`.
   - `value`: Literal operand (Numeric `Float/Int` e.g. `8.5`, or Literal `String` e.g. `'Computer Science'`).

4. **Order & Limit Slots**:
   - `order_by`: `{ "column": String, "direction": Enum {"ASC", "DESC"} }`
   - `limit`: Integer (`>= 1`, e.g., `top 5` -> `5`).

---

## 5. Output Data Contract: Intermediate Representation (IR)
The finalized output of the NLP engine satisfies the team integration contract (consumed by Member 2):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "QueryMind_Intermediate_Representation",
  "type": "object",
  "required": ["intent", "table", "columns", "conditions", "order_by", "limit"],
  "properties": {
    "intent": {
      "type": "string",
      "enum": ["RETRIEVAL", "FILTER", "COUNT", "AGGREGATION", "SORT"]
    },
    "table": {
      "type": "string",
      "enum": ["students", "courses", "departments", "enrollments"]
    },
    "columns": {
      "type": "array",
      "items": { "type": "string" }
    },
    "aggregation": {
      "type": ["object", "null"],
      "properties": {
        "function": { "type": "string", "enum": ["AVG", "COUNT", "MIN", "MAX", "SUM"] },
        "column": { "type": "string" }
      }
    },
    "conditions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["column", "operator", "value"],
        "properties": {
          "column": { "type": "string" },
          "operator": { "type": "string", "enum": [">", "<", ">=", "<=", "=", "!=", "LIKE"] },
          "value": { "type": ["string", "number"] }
        }
      }
    },
    "order_by": {
      "type": ["object", "null"],
      "properties": {
        "column": { "type": "string" },
        "direction": { "type": "string", "enum": ["ASC", "DESC"] }
      }
    },
    "limit": {
      "type": ["integer", "null"]
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    }
  }
}
```

---

## 6. Input Error Handling and Validation Boundaries

| Input Scenario | Validation Rule | Action / System Response |
| :--- | :--- | :--- |
| **Empty or Whitespace-only string** | `len(query.strip()) == 0` | Throw `EmptyQueryError`, prompt user for valid input |
| **Unrecognized domain entity** | Table cannot be inferred from tokens | Fallback to default or flag `AmbiguousEntityException` |
| **Comparison without target column** | e.g. `"Show students greater than 8"` | Infer best numeric column (`cgpa`) or request clarification |
| **Numeric format mismatch** | e.g. `"cgpa greater than eight point five"` | Verbal number parsing to float `8.5` |
| **Out-of-domain injection** | `"Drop database students;"` | NLP engine treats tokens as search terms, schema matcher ignores non-matching DDL, producing safe read-only IR |
