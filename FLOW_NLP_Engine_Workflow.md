# Flow File (Flowchart File)
## Project: QueryMind AI — Natural Language to SQL Assistant
### Module: Member 1 — NLP Module (Contract Version 1.0 Compliant)

---

## 1. System Pipeline Workflow (Mermaid)

```mermaid
flowchart TD
    Start([User Query String: 'Show students with CGPA above 8.5']) --> Ingest[1. Ingestion & Validation in process_natural_language]
    
    Ingest --> IsValid{Non-empty & length >= 3?}
    IsValid -- No --> ReturnErr[Return Structured Error JSON: UNSUPPORTED_QUERY]
    IsValid -- Yes --> Prep[2. Text Preprocessing Pipeline]

    subgraph Preprocessing [Text Preprocessing]
        Prep --> Clean[Normalize Quotes & Whitespace]
        Clean --> Tokenize[Tokenize Words & Comparison Operators]
        Tokenize --> Lemmatize[Lemmatize Plurals & Verbs]
    end

    Lemmatize --> Extract[3. Entity & Slot Extraction]

    subgraph Extraction [Slot & Entity Parsing]
        Extract --> Tab[Resolve Table: students]
        Extract --> Col[Resolve Columns: name, cgpa]
        Extract --> Cond[Resolve Conditions: cgpa > 8.5]
        Extract --> Join[Resolve Joins: []]
        Extract --> Agg[Resolve Aggregations: []]
        Extract --> Grp[Resolve Group By: []]
        Extract --> Ord[Resolve Order By: []]
        Extract --> Lim[Resolve Limit: null]
    end

    Tab --> IntentClass[4. Intent Classification Engine]
    Cond --> IntentClass
    Agg --> IntentClass
    
    IntentClass --> ResIntent[Intent = FILTER]
    
    ResIntent --> Assemble[5. Assemble Canonical Intermediate Representation]
    Col --> Assemble
    Cond --> Assemble
    Join --> Assemble
    Agg --> Assemble
    Grp --> Assemble
    Ord --> Assemble
    Lim --> Assemble

    Assemble --> Output([Return Canonical IR Dictionary])
    Output --> Handoff([Handoff to Member 2: process_ir])
```

---

## 2. Step-by-Step Execution Trace: 9 Mandatory Test Cases

| Case | Natural Language Input | Extracted Table | Intent | Conditions / Aggregations / Joins / Clauses |
|---|---|---|---|---|
| **1** | `"Show all students"` | `students` | `SELECT` | `conditions: []`, `order_by: []`, `limit: null` |
| **2** | `"Show students with CGPA above 8.5"` | `students` | `FILTER` | `conditions: [{"column": "cgpa", "operator": ">", "value": 8.5}]` |
| **3** | `"Find students from CSE department"` | `students` | `FILTER` | `conditions: [{"column": "department", "operator": "=", "value": "CSE"}]` |
| **4** | `"Show students in descending CGPA order"` | `students` | `SELECT` | `order_by: [{"column": "cgpa", "direction": "DESC"}]` |
| **5** | `"Show the top 5 students"` | `students` | `SELECT` | `order_by: [{"column": "cgpa", "direction": "DESC"}]`, `limit: 5` |
| **6** | `"Count all students"` | `students` | `AGGREGATE` | `aggregations: [{"function": "COUNT", "column": "*", "alias": "total_count"}]` |
| **7** | `"Find average CGPA"` | `students` | `AGGREGATE` | `aggregations: [{"function": "AVG", "column": "cgpa", "alias": "average_cgpa"}]` |
| **8** | `"Show students enrolled in each course"` | `students` | `SELECT` | `joins: [{"table": "enrollments", "type": "INNER", ...}]` |
| **9** | `"Find average CGPA department-wise"` | `students` | `AGGREGATE` | `aggregations: [AVG]`, `group_by: ["department"]` |
