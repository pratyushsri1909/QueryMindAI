# QueryMind AI — Natural Language to SQL Query Assistant
## Member 1 Deliverables: NLP Engine (Core Natural Language Understanding)

This repository contains the complete deliverables for **Member 1 (NLP Engine)** for the **QueryMind AI** project, as specified in the team implementation plan.

---

## 📁 Deliverables Directory & Documents

| Document / Deliverable | File Name | Description |
| :--- | :--- | :--- |
| **LID (Logical Input Design)** | [`LID_Logical_Input_Design.md`](LID_Logical_Input_Design.md) | Logical structure of inputs, sanitization, token structures, slot schemas, and IR JSON contract. |
| **HID (Hierarchical Input Design)** | [`HID_Hierarchical_Input_Design.md`](HID_Hierarchical_Input_Design.md) | Hierarchical module decomposition chart, submodules (1.0 to 6.0), and data flow model. |
| **Flow File (Flowchart File)** | [`FLOW_NLP_Engine_Workflow.md`](FLOW_NLP_Engine_Workflow.md) | Step-by-step lifecycle workflow diagrams (Mermaid & state diagrams) and execution traces. |
| **Decision File (Decision Logic)** | [`DECISION_Logic_File.md`](DECISION_Logic_File.md) | Decision logic tables for intent classification, schema mapping, operators, order/limit, and fallbacks. |
| **Code File (Source Code)** | [`nlp_engine/`](nlp_engine/) | Modular, production-ready Python package implementing the complete NLP Engine. |
| **Test Suite** | [`test_nlp_engine.py`](test_nlp_engine.py) | Comprehensive test suite verifying intent classification, slot extraction, and IR validation. |
| **Interactive Demo** | [`demo.py`](demo.py) | Interactive runner demonstrating queries turning into structured IR JSON. |

---

## 🏗️ Architecture of Member 1 (NLP Engine)

```
nlp_engine/
├── __init__.py           # Package exports (NLPEngine, Preprocessor, etc.)
├── schema_catalog.py     # Database schema, tables, columns, and domain synonym mappings
├── preprocessor.py       # Tokenizer, case normalizer, stop-word filter, lemmatizer, POS tagger
├── intent_classifier.py  # Intent classifier (RETRIEVAL, FILTER, COUNT, AGGREGATION, SORT)
├── entity_extractor.py   # Extracts tables, columns, relational operators, limits & ordering
├── ir_builder.py         # Assembles and validates the Intermediate Representation (IR) JSON contract
└── engine.py             # Main NLPEngine orchestrator pipeline
```

---

## 🚀 How to Run

### 1. Run Unit & Integration Tests
```bash
python test_nlp_engine.py
```

### 2. Run Interactive Live Demo
```bash
python demo.py
```

### 3. Use in Python Code
```python
from nlp_engine import NLPEngine
import json

engine = NLPEngine()

# Example query from the project specification:
query = "Show all students having CGPA greater than 8.5"
ir = engine.process_query(query)

print(json.dumps(ir, indent=2))
```

#### Output:
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
  "order_by": null,
  "limit": null,
  "confidence_score": 0.94
}
```

---

## 🤝 Integration Contract (Handoff to Member 2)
The NLP module converts natural language into the agreed-upon Intermediate Representation (IR) JSON, which **Member 2 (Database & SQL Engine)** consumes directly to construct safe PostgreSQL queries.
