# Logical Input Design (LID)
## Project: QueryMind AI — Natural Language to SQL Query Assistant
### Module: Member 1 — NLP Module (Contract Version 1.0 Compliant)

---

## 1. Overview & Purpose
The **Logical Input Design (LID)** specifies the logical characteristics, structural definitions, validation constraints, and lexical representations of all inputs processed by the **Member 1 (NLP Module)** under the **Team Integration Contract Version 1.0**.

Member 1 converts unstructured natural language questions in plain English into the Canonical **Intermediate Representation (IR)** JSON dictionary consumed by Member 2 (SQL Engine) and Member 3 (FastAPI & React UI).

---

## 2. Input Specifications

### 2.1 Primary Input: Natural Language Query
- **Field Name**: `query`
- **Function Signature**: `process_natural_language(query: str) -> dict`
- **Data Type**: `String (UTF-8)`
- **Origin**: End user via React UI $\rightarrow$ FastAPI Backend $\rightarrow$ `backend.app.nlp.process_natural_language(query)`.
- **Validation Constraints**:
  - Minimum Length: 3 characters (e.g. `"all students"`).
  - Maximum Length: 500 characters.
  - Allowed Characters: Alphanumeric (`a-z`, `A-Z`, `0-9`), standard punctuation (`.`, `,`, `?`, `'`, `"`, `>`, `<`, `=`, `!`, `-`), and whitespace.
  - Rejection / Sanitization: Rejects empty strings, whitespace-only queries, script injection tags, and control characters.

### 2.2 Domain Knowledge Base: PostgreSQL Database Schema (Contract Section 7)
All inputs are mapped against the 3 primary database tables:

1. **`students`**:
   - `student_id` (INTEGER - Primary Key)
   - `name` (VARCHAR)
   - `batch` (INTEGER)
   - `cgpa` (FLOAT)
   - `department` (VARCHAR)
2. **`courses`**:
   - `course_id` (INTEGER - Primary Key)
   - `course_name` (VARCHAR)
   - `credits` (INTEGER)
   - `department` (VARCHAR)
3. **`enrollments`**:
   - `enrollment_id` (INTEGER - Primary Key)
   - `student_id` (INTEGER - Foreign Key $\rightarrow$ `students.student_id`)
   - `course_id` (INTEGER - Foreign Key $\rightarrow$ `courses.course_id`)
   - `semester` (INTEGER)
   - `grade` (VARCHAR)

---

## 3. Logical Normalization & Lexicon Mapping

### 3.1 Intent Classification Mapping
| Logical Intent | Description | Linguistic Triggers |
| :--- | :--- | :--- |
| `SELECT` | Direct retrieval without conditional predicates, or order/limit/join queries | `"show"`, `"display"`, `"list"`, `"find all"`, `"top 5"`, `"descending order"` |
| `FILTER` | Filtering rows with WHERE predicate expressions | `"where"`, `"having"`, `"with"`, `"from CSE department"`, `"cgpa above 8.5"`, `">"`, `"<"`, `"="` |
| `AGGREGATE` | Mathematical aggregations or grouping | `"count"`, `"how many"`, `"average"`, `"avg"`, `"sum"`, `"max"`, `"min"`, `"department-wise"` |

### 3.2 Canonical Output Structure (Canonical IR Version 1.0)
Every valid input is converted into the exact contract schema:

```json
{
  "intent": "FILTER",
  "table": "students",
  "columns": ["name", "cgpa"],
  "conditions": [
    {
      "column": "cgpa",
      "operator": ">",
      "value": 8.5
    }
  ],
  "joins": [],
  "aggregations": [],
  "group_by": [],
  "order_by": [],
  "limit": null
}
```

### 3.3 Structured Error Schema (Contract Section 6)
When an input query cannot be understood or is invalid:
```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_QUERY",
    "message": "Input query cannot be empty or whitespace."
  }
}
```
