# Decision Logic File
## Project: QueryMind AI — Natural Language to SQL Query Assistant
### Module: Member 1 — NLP Engine & Natural Language Understanding

---

## 1. Overview
The **Decision Logic File** defines the exact conditions, branching rules, heuristics, and actions executed by the NLP engine when processing diverse user queries. It acts as the algorithmic blueprint governing how unstructured natural language tokens are mapped to deterministic intents, database entities, conditional operators, and aggregations.

---

## 2. Decision Logic Tables

### 2.1 Intent Classification Decision Table

| Rule ID | Trigger Condition (Tokens / Linguistic Patterns) | Secondary Condition | Action Taken / Inferred Intent |
| :--- | :--- | :--- | :--- |
| **INT-01** | Contains `"how many"`, `"count"`, `"number of"` | Any entity present | `intent = "COUNT"` |
| **INT-02** | Contains `"average"`, `"avg"`, `"mean"`, `"sum"`, `"total"`, `"min"`, `"max"`, `"highest"`, `"lowest"` | Followed by numeric column or quantifier | `intent = "AGGREGATION"` |
| **INT-03** | Contains `"sort"`, `"order by"`, `"rank"`, `"top"`, `"bottom"`, `"ascending"`, `"descending"` | Without standalone aggregation | `intent = "SORT"` |
| **INT-04** | Contains comparison triggers (`">"`, `"<"`, `"greater"`, `"less"`, `"above"`, `"below"`, `"having"`, `"where"`, `"equal"`, `"with"`) | Attribute + Operator + Value detected | `intent = "FILTER"` |
| **INT-05** | Contains generic retrieval verbs (`"show"`, `"list"`, `"display"`, `"get"`, `"find"`) | No conditional predicates or aggregates | `intent = "RETRIEVAL"` |
| **INT-06** | No recognizable intent keyword detected | Valid table entity found | Default to `intent = "RETRIEVAL"` |
| **INT-07** | Query is completely empty or unrecognizable noise | `len(tokens) == 0` | Action: Raise `EmptyQueryException` |

---

### 2.2 Table and Entity Resolution Decision Table

| Rule ID | Input Token Match / Synonyms | Target Database Table | Inferred Default Columns |
| :--- | :--- | :--- | :--- |
| **TAB-01** | `"student"`, `"students"`, `"pupil"`, `"scholars"`, `"candidate"` | `students` | `["id", "name", "cgpa", "email"]` |
| **TAB-02** | `"course"`, `"courses"`, `"subject"`, `"subjects"`, `"class"` | `courses` | `["course_id", "course_name", "credits"]` |
| **TAB-03** | `"department"`, `"departments"`, `"dept"`, `"branch"`, `"stream"` | `departments` | `["dept_id", "dept_name", "building"]` |
| **TAB-04** | `"enroll"`, `"enrollment"`, `"enrolled"`, `"grade"`, `"score"` | `enrollments` | `["enrollment_id", "student_id", "course_id", "grade"]` |
| **TAB-05** | Table not explicitly named, but column `"cgpa"` or `"gpa"` exists | `students` (inferred) | `["name", "cgpa"]` |
| **TAB-06** | Table not explicitly named, but column `"credits"` exists | `courses` (inferred) | `["course_name", "credits"]` |
| **TAB-07** | Multiple tables detected (e.g. `"students in Computer Science department"`) | Primary: `students`, Related: `departments` | Join condition flagged for Member 2 |

---

### 2.3 Relational Operator Decision Logic Table

| Rule ID | Text Pattern in Query | Resolved Relational Operator | Example Token Context |
| :--- | :--- | :--- | :--- |
| **OP-01** | `"greater than"`, `"more than"`, `"above"`, `"exceeding"`, `">"` | `>` | `"cgpa greater than 8.5"` |
| **OP-02** | `"greater than or equal to"`, `"at least"`, `"minimum of"`, `">="` | `>=` | `"cgpa at least 7.0"` |
| **OP-03** | `"less than"`, `"fewer than"`, `"below"`, `"under"`, `"<"` | `<` | `"credits less than 4"` |
| **OP-04** | `"less than or equal to"`, `"at most"`, `"maximum of"`, `"<="` | `<=` | `"cgpa at most 9.0"` |
| **OP-05** | `"equals"`, `"equal to"`, `"is"`, `"with"`, `"=="`, `"="` | `=` | `"department is Computer Science"` |
| **OP-06** | `"not equal to"`, `"not"`, `"different from"`, `"!="`, `"<>"` | `!=` | `"department not Civil"` |
| **OP-07** | `"starts with"`, `"ends with"`, `"contains"`, `"like"` | `LIKE` | `"name starts with 'A'"` |

---

### 2.4 Ordering & Limit Decision Logic Table

| Rule ID | Trigger Expression | `order_by.direction` | `limit` Value | Inferred Target Column |
| :--- | :--- | :--- | :--- | :--- |
| **ORD-01** | `"top {N}"` (e.g. `"top 5"`) | `"DESC"` | `N` (e.g. `5`) | Extracted numeric column (e.g. `cgpa`) |
| **ORD-02** | `"highest"`, `"best"`, `"maximum"` | `"DESC"` | `1` (if no N given) | Extracted numeric column |
| **ORD-03** | `"bottom {N}"`, `"lowest {N}"` | `"ASC"` | `N` | Extracted numeric column |
| **ORD-04** | `"ascending"`, `"asc"`, `"alphabetical"` | `"ASC"` | `null` | Contextual sort column |
| **ORD-05** | `"descending"`, `"desc"` | `"DESC"` | `null` | Contextual sort column |
| **ORD-06** | `"limit {N}"`, `"first {N}"` | Direction preserved or `null` | `N` | Contextual column |

---

## 3. Decision Logic Flow Tree

```
[Start Input Evaluation]
       │
       ├─► (Q1: Is query empty or whitespace?)
       │      ├─► YES: Raise EmptyQueryError
       │      └─► NO:  Proceed to normalization
       │
       ├─► (Q2: What is the primary query intention?)
       │      ├─► Contains "count" / "how many" ──────► INTENT = COUNT
       │      ├─► Contains "average" / "max" / "min" ──► INTENT = AGGREGATION
       │      ├─► Contains "top N" / "sort" / "rank" ──► INTENT = SORT
       │      ├─► Contains comparison (> / < / =) ────► INTENT = FILTER
       │      └─► Default fallback ────────────────────► INTENT = RETRIEVAL
       │
       ├─► (Q3: Which database table is referenced?)
       │      ├─► Matches "student(s)" ────────────────► TABLE = students
       │      ├─► Matches "course(s)" ─────────────────► TABLE = courses
       │      ├─► Matches "department(s)" ─────────────► TABLE = departments
       │      ├─► Matches "enrollment(s)" ─────────────► TABLE = enrollments
       │      └─► Entity absent: Infer via column name ─► TABLE = (Inferred)
       │
       ├─► (Q4: Are there condition expressions?)
       │      ├─► Found operator + value ──────────────► Add to conditions[] list
       │      └─► None ────────────────────────────────► conditions = []
       │
       ├─► (Q5: Are there ordering or limit quantifiers?)
       │      ├─► Found "top N" / "highest" ───────────► order_by = {col, DESC}, limit = N
       │      ├─► Found "bottom N" / "lowest" ─────────► order_by = {col, ASC}, limit = N
       │      └─► None ────────────────────────────────► order_by = null, limit = null
       │
       └─► (Q6: Validate assembled IR JSON)
              ├─► Compliant with IR Contract ──────────► Emit Valid IR JSON (Status 200)
              └─► Missing required fields ─────────────► Apply fallback heuristics
```

---

## 4. Ambiguity Resolution & Fallback Matrix

1. **Paraphrase Handling**:
   - `"List all learners with GPA over 8"`
   - `learners` -> Synonyms mapping resolves to `students`.
   - `GPA` -> Resolves to `cgpa`.
   - `over` -> Resolves to operator `>`.
   - Result: Equivalent IR to `"Show all students having CGPA greater than 8"`.

2. **Omission of Target Column in Condition**:
   - Example: `"Show students greater than 8"`
   - Decision Logic: Query targets table `students` with numeric predicate `8`. Check table schema for numeric attributes: `cgpa`.
   - Action: Bind condition to `cgpa > 8`. Mark confidence score as `0.85` (deducted for inference).

3. **Multi-Condition Joining**:
   - Example: `"Students with CGPA greater than 8 and admission year 2024"`
   - Decision Logic: Detect conjunction `"and"`. Extract multiple conditions into list:
     - `[{"column": "cgpa", "operator": ">", "value": 8}, {"column": "admission_year", "operator": "=", "value": 2024}]`
