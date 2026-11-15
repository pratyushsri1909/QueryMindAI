# QueryMind AI — Member 1: NLP Module
### Team Integration Contract Version 1.0 Compliant

---

## 📌 Overview
This module represents the complete, independent implementation of **Member 1 (NLP Module)** for the **QueryMind AI** natural language-to-SQL system.

The module is responsible for:
1. Ingesting plain English questions from users.
2. Performing query preprocessing (tokenization, cleaning, lemmatization, POS tagging).
3. Classifying user intent (`SELECT`, `FILTER`, `AGGREGATE`).
4. Extracting schema entities (tables: `students`, `courses`, `enrollments`, columns, predicates, joins, aggregations, group by, order by, limit).
5. Outputting the standardized **Intermediate Representation (IR)** JSON dictionary or structured error response.

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   └── nlp/
│   │       ├── __init__.py           # Exports public function: process_natural_language
│   │       ├── processor.py          # Main NLPProcessor and process_natural_language implementation
│   │       ├── preprocessing.py      # Tokenizer, stop-word filter, lemmatizer, POS tagger
│   │       ├── intent_classifier.py  # Classifies into SELECT, FILTER, AGGREGATE
│   │       ├── entity_extractor.py   # Extracts tables, columns, conditions, joins, aggregations
│   │       └── schema.py             # Schema definition & synonyms for students, courses, enrollments
│   └── tests/
│       └── test_nlp.py               # Integration test for backend test runners
├── test_nlp_engine.py                # 10 test cases covering all 9 mandatory contract queries
├── demo.py                           # Interactive CLI demo showcasing all 9 test queries
├── LID_Logical_Input_Design.md       # Logical Input Design document
├── HID_Hierarchical_Input_Design.md  # Hierarchical Input Design document
├── FLOW_NLP_Engine_Workflow.md       # Flowchart and workflow document
└── DECISION_Logic_File.md            # Decision logic and decision tables document
```

---

## 🔌 Public Interface & How to Invoke

In compliance with **Section 3 of Team Integration Contract Version 1.0**:

```python
from backend.app.nlp import process_natural_language

# Example query:
query = "Show students with CGPA above 8.5"

# Generate Canonical IR:
ir = process_natural_language(query)
print(ir)
```

### Sample Input & Output

#### Input:
```text
Show students with CGPA above 8.5
```

#### Output (Canonical IR Version 1.0):
```json
{
  "intent": "FILTER",
  "table": "students",
  "columns": [
    "name",
    "cgpa"
  ],
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

#### Error Output Example:
```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_QUERY",
    "message": "Input query cannot be empty or whitespace."
  }
}
```

---

## 🧪 Mandatory Test Cases (Contract Section 9)

Run the test suite using:
```bash
python test_nlp_engine.py
```

All 9 mandatory queries from the Team Integration Contract pass with 100% success:
1. `Show all students` $\rightarrow$ `intent: SELECT`, `table: students`
2. `Show students with CGPA above 8.5` $\rightarrow$ `intent: FILTER`, `cgpa > 8.5`
3. `Find students from CSE department` $\rightarrow$ `intent: FILTER`, `department = 'CSE'`
4. `Show students in descending CGPA order` $\rightarrow$ `order_by: [{"column": "cgpa", "direction": "DESC"}]`
5. `Show the top 5 students` $\rightarrow$ `limit: 5`, `order_by: DESC`
6. `Count all students` $\rightarrow$ `intent: AGGREGATE`, `COUNT(*)`
7. `Find average CGPA` $\rightarrow$ `intent: AGGREGATE`, `AVG(cgpa)`
8. `Show students enrolled in each course` $\rightarrow$ `joins: [enrollments INNER JOIN]`
9. `Find average CGPA department-wise` $\rightarrow$ `group_by: ["department"]`, `AVG(cgpa)`
