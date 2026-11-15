# Decision Logic File
## Project: QueryMind AI — Natural Language to SQL Assistant
### Module: Member 1 — NLP Module (Contract Version 1.0 Compliant)

---

## 1. Intent Classification Decision Logic

The Team Integration Contract Version 1.0 defines three canonical intent types: `SELECT`, `FILTER`, and `AGGREGATE`.

```
                  ┌───────────────────────────────┐
                  │ Does query contain aggregate  │
                  │ function (COUNT, AVG, SUM,    │
                  │ MIN, MAX) or GROUP BY?        │
                  └──────────────┬────────────────┘
                                 │
                 YES ────────────┴──────────── NO
                  │                            │
                  ▼                            ▼
         ┌─────────────────┐       ┌───────────────────────┐
         │ INTENT =        │       │ Does query contain    │
         │ 'AGGREGATE'     │       │ conditional filters   │
         └─────────────────┘       │ (WHERE predicates)?   │
                                   └───────────┬───────────┘
                                               │
                               YES ────────────┴──────────── NO
                                │                            │
                                ▼                            ▼
                       ┌─────────────────┐          ┌─────────────────┐
                       │ INTENT =        │          │ INTENT =        │
                       │ 'FILTER'        │          │ 'SELECT'        │
                       └─────────────────┘          └─────────────────┘
```

---

## 2. Decision Logic Tables

### 2.1 Table and Entity Resolution
| Condition in Input Query | Resolved Table | Default Projected Columns |
|---|---|---|
| Query mentions `"student"`, `"students"`, `"pupil"`, `"scholar"` | `students` | `["name", "cgpa"]` (or `["student_id", "name", ...]`) |
| Query mentions `"course"`, `"courses"`, `"subject"`, `"classes"` | `courses` | `["course_name", "credits"]` |
| Query mentions `"enroll"`, `"enrollment"`, `"grade"`, `"score"` | `enrollments` | `["enrollment_id", "student_id", "course_id", "grade"]` |
| Primary table is `students` and query mentions `"course"` or `"enrolled"` | Primary: `students` | Resolves `INNER JOIN enrollments` on `students.student_id = enrollments.student_id` |

### 2.2 Operator and Condition Resolution
| Condition Trigger | Relational Operator | Example Context | Condition Object Added |
|---|---|---|---|
| `"above"`, `"greater than"`, `">"` | `>` | `"cgpa above 8.5"` | `{"column": "cgpa", "operator": ">", "value": 8.5}` |
| `"below"`, `"less than"`, `"<"` | `<` | `"credits below 4"` | `{"column": "credits", "operator": "<", "value": 4}` |
| `"at least"`, `">="` | `>=` | `"cgpa at least 7.0"` | `{"column": "cgpa", "operator": ">=", "value": 7.0}` |
| `"from {DEPT} department"` | `=` | `"from CSE department"` | `{"column": "department", "operator": "=", "value": "CSE"}` |

### 2.3 Aggregations and Grouping Resolution
| Trigger Expression | Aggregation Function | Group By Column | Alias |
|---|---|---|---|
| `"count"`, `"how many"` | `COUNT` on `*` | `[]` | `"total_count"` |
| `"average"`, `"avg"` | `AVG` on target column | `[]` | `"average_{column}"` |
| `"department-wise"`, `"by department"` | Contextual function | `["department"]` | Standard alias |
| `"top {N}"`, `"descending"` | Sorting on target column | `[]` | `order_by: [{"column": "cgpa", "direction": "DESC"}]`, `limit: N` |

---

## 3. Error Handling Decision Logic

| Scenario | Condition | System Action / Response |
|---|---|---|
| Empty or whitespace string | `len(query.strip()) == 0` | Return `{"success": false, "error": {"code": "UNSUPPORTED_QUERY", "message": "Input query cannot be empty or whitespace."}}` |
| Query length $< 3$ characters | `len(cleaned) < 3` | Return `{"success": false, "error": {"code": "UNSUPPORTED_QUERY", "message": "Query is too short to extract meaningful intent."}}` |
| Exception during extraction | Unhandled parsing error | Return `{"success": false, "error": {"code": "INVALID_IR", "message": "..."}}` |
