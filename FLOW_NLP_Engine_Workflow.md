# Flow File (Flowchart File)
## Project: QueryMind AI — Natural Language to SQL Query Assistant
### Module: Member 1 — NLP Engine & Natural Language Understanding

---

## 1. Overview
The **Flow File** depicts the operational lifecycle and step-by-step decision workflow of the **Member 1 (NLP Engine)**. It maps the end-to-end journey of an input query from the moment an end-user types a natural language question until a fully validated Intermediate Representation (IR) JSON is produced for the SQL Engine (Member 2).

---

## 2. System Workflow Diagram (Mermaid)

```mermaid
flowchart TD
    Start([User Submits Natural Language Query]) --> Step1[1. Input Ingestion & Sanitization]
    
    Step1 --> CheckEmpty{Query valid & non-empty?}
    CheckEmpty -- No --> ErrorEmpty[Throw InputValidationError / Prompt User]
    CheckEmpty -- Yes --> Step2[2. Text Preprocessing Pipeline]

    subgraph Preprocessing_Pipeline [Text Preprocessing Pipeline]
        Step2 --> Step2A[Case Normalization to Lowercase]
        Step2A --> Step2B[Punctuation & Symbol Standardization]
        Step2B --> Step2C[Lexical Tokenization]
        Step2C --> Step2D[Stop-Word Filtering with Operator Preservation]
        Step2D --> Step2E[Lemmatization & POS Tagging]
    end

    Step2E --> Step3[3. Parallel Feature Extraction]

    subgraph Feature_Extraction [Extraction & Classification]
        Step3 --> Step3A[3.1 Intent Classification Engine]
        Step3 --> Step3B[3.2 Schema Entity Resolution]
        Step3 --> Step3C[3.3 Condition & Predicate Extraction]
        Step3 --> Step3D[3.4 Aggregation & Function Parsing]
        Step3 --> Step3E[3.5 Ordering & Limit Parsing]
    end

    Step3A --> Merge[4. Intermediate Representation Builder]
    Step3B --> Merge
    Step3C --> Merge
    Step3D --> Merge
    Step3E --> Merge

    Merge --> Step4[Assemble Standard IR Dictionary]
    Step4 --> CheckSchema{Valid IR Structure & Schema?}
    
    CheckSchema -- No / Low Confidence --> StepFallback[Apply Fallback Heuristics & Defaults]
    StepFallback --> CheckSchema2{Recoverable?}
    CheckSchema2 -- No --> ErrorIR[Emit AmbiguousQueryError JSON]
    CheckSchema2 -- Yes --> Step5[Calculate Confidence Score]
    
    CheckSchema -- Yes --> Step5
    Step5 --> Deliverable([Output: Validated IR JSON])
    Deliverable --> Member2[Handoff to Member 2: SQL Engine]
```

---

## 3. Step-by-Step Workflow Execution Trace

### Phase 1: Input Ingestion & Sanitization
1. **Entry**: User inputs string e.g., `"Show all students having CGPA greater than 8.5"`.
2. **Length & Type Check**: Asserts query is a non-empty string with length between 3 and 500 characters.
3. **Punctuation Clean**: Eliminates trailing commas, question marks, and unifies comparative symbols.

### Phase 2: Preprocessing Pipeline
1. **Normalization**: `"show all students having cgpa greater than 8.5"`
2. **Tokenization**: `['show', 'all', 'students', 'having', 'cgpa', 'greater', 'than', '8.5']`
3. **Stop-word Cleaning**: Drops conversational noise like `'all'`; preserves contextual triggers `'greater'`, `'than'`, `'having'`.
4. **Lemmatization**: Maps `'students'` -> `'student'`, maintaining lemma tokens alongside original tokens.
5. **POS Tagging**: Identifies `'students'` (Noun), `'cgpa'` (Noun), `'greater'` (Comparative Adjective), `'8.5'` (Number).

### Phase 3: Extraction & Intent Resolution
1. **Intent Classification**:
   - Detection of conditional markers (`"having"`, `"greater than"`) classifies primary intent as **`FILTER`**.
2. **Schema Resolution**:
   - Detects entity token `'student'` / `'students'`. Matches with database table **`students`**.
   - Detects attribute `'cgpa'`. Matches with table column **`cgpa`**.
   - Default projection attributes selected: `["name", "cgpa"]`.
3. **Condition Extraction**:
   - Identifies comparison phrase `"greater than"` -> relational operator **`>`**.
   - Identifies numeric literal `'8.5'` -> float value **`8.5`**.
   - Associates column `'cgpa'` with operator `>` and value `8.5`.
   - Condition object created: `{"column": "cgpa", "operator": ">", "value": 8.5}`.
4. **Ordering & Limit Extraction**:
   - No ordering keywords detected -> `order_by: null`.
   - No explicit limit detected -> `limit: null`.

### Phase 4: Intermediate Representation (IR) Assembly
1. Consolidates extracted components into the agreed JSON schema format:
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
  "order_by": null,
  "limit": null,
  "confidence_score": 0.95
}
```

### Phase 5: Schema Validation & Delivery
1. Validates required keys (`intent`, `table`, `columns`, `conditions`, `order_by`, `limit`).
2. Checks data types and allowed operator enums.
3. Computes confidence score (0.95).
4. Hands over JSON payload to Member 2 (SQL Engine).

---

## 4. Alternative Workflows & Exception Handling

```mermaid
stateDiagram-v2
    [*] --> Ingestion
    Ingestion --> Preprocessing: Valid Input
    Ingestion --> InvalidInputError: Empty or Malformed Input

    Preprocessing --> FeatureExtraction: Clean Tokens
    FeatureExtraction --> SchemaMapping
    
    SchemaMapping --> IRBuilder: Entity Found
    SchemaMapping --> AmbiguityHandler: Entity Missing or Unknown
    
    AmbiguityHandler --> IRBuilder: Default Entity Inferred
    AmbiguityHandler --> UnresolvedError: Unrecoverable
    
    IRBuilder --> SchemaValidation
    SchemaValidation --> OutputReady: Schema Pass
    SchemaValidation --> OutputError: Schema Fail
    
    OutputReady --> [*]
    InvalidInputError --> [*]
    UnresolvedError --> [*]
    OutputError --> [*]
```
