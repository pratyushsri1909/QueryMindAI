# Logical Input Design (LID) — QueryMind AI

## 1. Project Overview

**QueryMind AI** is an intelligent Natural Language to SQL (NL-to-SQL) query assistant designed to bridge the technical divide between non-technical domain users and relational databases (specifically PostgreSQL). Instead of requiring users to master SQL syntax, database schemas, relational joins, and aggregation functions, QueryMind AI interprets human language queries, parses semantic intent and constraints, maps them to an underlying schema, generates syntactically valid and authorized SQL, and presents query results in an interactive interface.

> **Status Notice:**
> - **Implemented (Day 1):** FastAPI server foundation, root (`/`) and health check (`/health`) endpoints, core directory structure, and automated unit test suite.
> - **Planned (Future Iterations):** Natural language parsing pipeline, semantic entity extraction, schema mapping dictionary, SQL generation engine, and database query execution.

---

## 2. Main Input: Natural Language Query

The primary input mechanism for QueryMind AI is an unconstrained, free-text natural language query submitted by the end user via the web client interface or REST API.

- **Primary Persona:** Business analysts, university administrators, faculty members, and students seeking information from academic databases without writing SQL.
- **Input Modality:** Text string via HTTP POST request payload (`application/json`).
- **Target Domain (Initial Scope):** Academic Management System consisting of tables such as `students`, `courses`, `departments`, and `enrollments`.

---

## 3. Input Types and Formats

| Attribute | Specification | Status |
| :--- | :--- | :--- |
| **Data Format** | JSON payload over HTTP POST | Planned |
| **Payload Schema** | `{"query": string, "database_id": optional string}` | Proposed Interface |
| **Character Encoding** | UTF-8 | Planned Standard |
| **Text Constraints** | Min length: 3 characters; Max length: 500 characters | Planned Rule |
| **Case Sensitivity** | Case-insensitive normalization during preprocessing | Planned Rule |
| **Language Support** | English (Standard and conversational phrasing) | Planned Scope |

---

## 4. Example User Queries

The system is designed to handle queries spanning multiple grammatical structures and analytical operations:

1. **Simple Selection:**
   - *"List all students."*
   - *"Show all courses offered by the Computer Science department."*
2. **Conditional Filtering:**
   - *"Show students whose CGPA is greater than 8.5."*
   - *"Find courses with credits equal to 4."*
3. **Sorting and Ordering:**
   - *"List students ordered by graduation year descending."*
   - *"Show top 5 students with the highest CGPA."*
4. **Aggregation and Metrics:**
   - *"How many students are enrolled in each department?"*
   - *"What is the average CGPA of students in the Electrical Engineering department?"*
5. **Relational Joins:**
   - *"Show the names of students enrolled in Advanced Database Systems."*
   - *"List all courses taught by department heads."*

---

## 5. Logical Input Components

When a natural language query is analyzed, the system decomposes the unstructured string into discrete logical tokens and semantic components:

1. **Intent / Action:**
   - Defines the primary database verb or analytical action (`SELECT`, `FILTER`, `COUNT`, `AGGREGATION`, `SORT`, `JOIN`).
2. **Target Entity (Table):**
   - The primary subject of interest (`students`, `courses`, `departments`, `enrollments`).
3. **Attributes (Columns / Fields):**
   - The specific characteristics or values requested (`first_name`, `last_name`, `cgpa`, `department_name`, `credits`).
4. **Relational Operators:**
   - Comparison mechanisms (`=`, `!=`, `>`, `<`, `>=`, `<=`, `IN`, `LIKE`, `BETWEEN`).
5. **Filter Values (Literals):**
   - Concrete scalar bounds or string criteria (`8.5`, `'Computer Science'`, `2024`).
6. **Modifiers & Ordering:**
   - Sorting directions (`ASC`, `DESC`), limits (`LIMIT n`), grouping (`GROUP BY`).

---

## 6. Input Validation Requirements

Before passing input to downstream NLP models or SQL generation pipelines, strict input validation must be enforced at the API boundary:

1. **Presence & Non-Emptiness:**
   - Reject empty strings, null values, or strings consisting entirely of whitespace.
2. **Length Guardrails:**
   - Enforce a minimum length of 3 characters (e.g., prevent single-character typos) and maximum length of 500 characters (mitigate denial-of-service / resource exhaustion).
3. **Sanitization & Security Filter:**
   - Strip non-printable ASCII characters and control characters.
   - Detect and flag explicit SQL injection vectors (e.g., `DROP TABLE`, `UNION SELECT`, `--`, `;`, `/* */`) at the query level before parsing.
4. **Character Set Validation:**
   - Restrict characters to alphanumeric symbols, standard punctuation, and basic mathematical signs (`?`, `.`, `,`, `>`, `<`, `=`, `!`, `'`, `"`).

---

## 7. Input-to-Output Relationship

The transformation lifecycle maps user queries through progressive intermediate states:

```
[Raw Natural Language String]
          ↓ (API Ingestion & Validation)
[Sanitized Natural Language Query]
          ↓ (NLP Processing Pipeline)
[Intermediate Representation (IR) JSON]
          ↓ (Schema Mapping & SQL Generation)
[Validated Read-Only SQL Query]
          ↓ (PostgreSQL Execution)
[Structured Tabular Result Set / JSON]
```

### Detailed Example Walkthrough

- **Raw User Input:**  
  `"Show students whose CGPA is greater than 8.5."`

- **Logical Interpretation:**
  - **Operation:** `FILTER` (with `SELECT`)
  - **Entity / Table:** `students`
  - **Attribute / Column:** `cgpa`
  - **Operator:** Greater than (`>`)
  - **Value:** `8.5`

- **Generated SQL Target (Planned):**
  ```sql
  SELECT * FROM students WHERE cgpa > 8.5;
  ```

- **Output to Frontend (Planned):**
  Tabular data containing student records matching the filter criteria, alongside the generated SQL explanation.

---

## 8. Input Format Expected by the NLP Engine

The NLP Engine (managed by Member 1) will receive a structured internal request object from the API layer:

```json
{
  "query_text": "Show students whose CGPA is greater than 8.5.",
  "context": {
    "target_schema": "public",
    "user_id": "usr_94821",
    "session_id": "sess_01HXYZ99"
  }
}
```

*Note: This contract defines the interface between Member 3 (Backend API) and Member 1 (NLP Engine).*

---

## 9. Expected Structured Representation (IR) Passed to the SQL Engine

> **Important Notice:** The JSON schema below represents the **proposed contract and interface** between the NLP Engine (Member 1) and the SQL Engine (Member 2). It is not yet implemented in Day 1.

```json
{
  "version": "1.0",
  "intent": "FILTER",
  "entities": [
    {
      "name": "students",
      "alias": "s"
    }
  ],
  "select_attributes": [
    {
      "entity": "students",
      "attribute": "*"
    }
  ],
  "filters": [
    {
      "entity": "students",
      "attribute": "cgpa",
      "operator": ">",
      "value": 8.5,
      "data_type": "float"
    }
  ],
  "aggregations": [],
  "ordering": [],
  "limit": null
}
```

### Explanation of Contract Fields:
- `version`: Protocol version for intermediate representation evolution.
- `intent`: Primary analytical intention classified by NLP.
- `entities`: Database entities recognized from the input text.
- `select_attributes`: Explicit columns or wildcard projected in the query.
- `filters`: Condition clauses capturing attributes, operators, typed values, and logical relations.
- `aggregations`: Analytical functions (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`) and group-by columns.
- `ordering`: Sort order specifications (`column`, `direction`).
- `limit`: Numerical row limit if requested by the user query.
