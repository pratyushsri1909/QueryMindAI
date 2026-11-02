# QueryMind AI — Natural Language to SQL Query Assistant

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646cff.svg?logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38bdf8.svg?logo=tailwindcss)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

QueryMind AI is an academic and enterprise-oriented Natural Language to SQL (NL-to-SQL) assistant. It allows non-technical stakeholders—such as university administrators, researchers, students, and business analysts—to query relational databases (PostgreSQL) using intuitive, plain English rather than manually composing complex SQL queries.

---

## 1. Project Objective

Relational databases store vast amounts of mission-critical information, yet accessing this data often requires specialized proficiency in SQL syntax, relational algebra, and physical schema topology. QueryMind AI eliminates this barrier by providing:

1. **Semantic Query Translation:** Translating natural-language questions into syntactically valid ANSI/PostgreSQL queries.
2. **Read-Only Safety & Guardrails:** Enforcing strict AST validation to guarantee data security and prevent unauthorized schema or data mutations.
3. **Transparent Execution:** Exposing generated SQL side-by-side with execution results to foster user trust and verification.
4. **Accessible Interface:** Presenting tabular results through an interactive web-based interface.

---

## 2. End-to-End Pipeline Architecture (Day 2 Prototype)

QueryMind AI connects natural language to database execution through a modular five-stage processing pipeline:

```text
[ Natural Language Input ]
           ↓
[ FastAPI Backend (POST /api/v1/query) ]
           ↓
[ Mock NLP Module ] ──→ [ Intermediate Representation (IR) ]
                                      ↓
                            [ Mock SQL Engine ] ──→ [ Generated SQL + Mock Results ]
                                                               ↓
                                                    [ React + Vite Web UI ]
```

> **Important Architecture & Integration Notice:**  
> The current Day 2 release implements the complete **end-to-end integration prototype** using **deterministic MOCK NLP and MOCK SQL Engine modules**. This prototype validates the full-stack request/response lifecycle, Pydantic schemas, and frontend presentation. It does **not** connect to a physical PostgreSQL instance, nor does it perform machine learning inference.

---

## 3. Technology Stack

### Backend:
- **Language & Runtime:** Python 3.11
- **API Framework:** FastAPI & Uvicorn (ASGI)
- **Data Modeling & Validation:** Pydantic v2
- **Testing:** Pytest, HTTPX (`fastapi.testclient.TestClient`)
- **Future ML/NLP Integration (Member 1):** NLTK, spaCy, Scikit-learn
- **Future DB/SQL Engine (Member 2):** PostgreSQL, SQLAlchemy, `psycopg` (binary), SQLGlot (AST parsing)

### Frontend:
- **Library & Build Tool:** React 18, Vite 6
- **Styling:** Tailwind CSS, PostCSS, Autoprefixer
- **Icons:** Lucide React
- **API Communication:** Dedicated Fetch Service (`queryService.js`)

---

## 4. Team Architecture & Responsibilities

QueryMind AI is collaboratively developed by a three-member engineering team with clear boundaries of concern:

| Team Member | Domain Responsibility | Current Deliverables & Scope |
| :--- | :--- | :--- |
| **Member 1** | **NLP Engine** | Preprocessing, tokenization, intent classification, entity extraction, and Intermediate Representation (IR) generation. *(Day 2: Mock NLP integration prototype)* |
| **Member 2** | **Database & SQL Engine** | Schema mapping catalog, SQL generation, SQLGlot AST validation, read-only security enforcement, and PostgreSQL execution. *(Day 2: Mock SQL generation and fixture execution)* |
| **Member 3 (Current)** | **Backend, Frontend & Integration** | FastAPI architecture, Pydantic contracts, CORS configuration, automated test suites, React + Vite developer dashboard, and full-stack integration. *(Day 1 & Day 2 Completed)* |

---

## 5. System Design Documentation Index

Comprehensive engineering specifications are cataloged inside the [`docs/`](docs/) directory:

| Artifact | Document Description | Direct Link |
| :--- | :--- | :--- |
| **LID** | **Logical Input Design** — Defines logical inputs, validation constraints, query types, and the NLP-to-SQL Intermediate Representation contract. | [Read LID](docs/LID.md) |
| **HID** | **Hierarchical Input Design** — Decomposes the system into functional hierarchies, modules, dependencies, and team ownership. | [Read HID](docs/HID.md) |
| **Code File** | **Source Code Design** — Catalogs repository structure, package responsibilities, coding standards, and codebase snippets. | [Read Code File](docs/CODE_FILE.md) |
| **Flow File** | **System Workflow** — Step-by-step pipeline from natural language input to tabular display, accompanied by a GitHub Mermaid diagram. | [Read Flow File](docs/FLOW_FILE.md) |
| **Decision File** | **Decision Logic** — Defines business rules, decision tables, error trees, and pseudocode across all five processing stages. | [Read Decision File](docs/DECISION_FILE.md) |

---

## 6. Implementation Status

### Day 1 Deliverables (Completed):
- [x] Git branch workflow isolated on `feature/application`.
- [x] Modular project directory structure (`backend/`, `frontend/`, `datasets/`, `docs/`).
- [x] Python 3.11 virtual environment and dependency specifications (`backend/requirements.txt`).
- [x] FastAPI application initialized with OpenAPI metadata (`backend/app/main.py`).
- [x] Root endpoint (`GET /`) and Health Check endpoint (`GET /health`).
- [x] Automated unit test suite (`backend/tests/test_main.py`).
- [x] System design documentation suite (LID, HID, Code File, Flow File, Decision File).

### Day 2 Deliverables (Completed):
- [x] Pydantic request/response contract models (`backend/app/schemas/query.py`).
- [x] Query validation: rejection of empty, whitespace-only, and >500 character queries.
- [x] Deterministic Mock NLP module (`backend/app/nlp/mock_nlp.py`) generating structured IR objects.
- [x] Deterministic Mock SQL Engine (`backend/app/sql_engine/mock_sql_engine.py`) generating ANSI SQL and mock results.
- [x] Full-stack REST API endpoint `POST /api/v1/query` (`backend/app/api/routes.py`).
- [x] FastAPI CORS configuration allowing local frontend development origins (`http://localhost:5173`).
- [x] Modern light-theme React + Vite web dashboard (`frontend/`) featuring:
  - Header with live backend health indicator and Mock Pipeline badge.
  - Natural language input with suggestion pills and character counter.
  - Generated SQL panel with one-click clipboard copy.
  - Dynamic results table with row count and formatted records.
  - Execution summary cards (intent, status, mock latency).
  - Expandable Intermediate Representation (IR) contract JSON viewer.
  - Robust error states (offline banner, API validation alerts).
- [x] 14 automated backend unit and integration tests passing (`pytest -v`).

### Planned (Future Iterations):
- [ ] Member 1: Real spaCy/NLTK pipeline and machine learning intent classifier.
- [ ] Member 2: PostgreSQL database container, SQLGlot AST validation, and physical query executor.

---

## 7. API Endpoint Documentation

### Base URL
`http://localhost:8000`

### 1. `POST /api/v1/query` — Process Natural Language Query
Transforms a natural language string into ANSI/PostgreSQL via the mock pipeline and returns tabular execution results.

#### Request Headers
```http
Content-Type: application/json
Accept: application/json
```

#### Request Payload
```json
{
  "query": "Show students with CGPA above 8.5"
}
```

#### Request Validation Rules:
- `query` field is required.
- Query cannot be empty or contain solely whitespace.
- Query length must not exceed 500 characters.

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "message": "Query processed successfully",
  "original_query": "Show students with CGPA above 8.5",
  "intent": "FILTER",
  "ir": {
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
    "limit": null
  },
  "generated_sql": "SELECT name, cgpa FROM students WHERE cgpa > 8.5;",
  "execution": {
    "status": "mock_success",
    "columns": [
      "name",
      "cgpa"
    ],
    "rows": [
      [
        "Aarav",
        9.1
      ],
      [
        "Diya",
        8.8
      ],
      [
        "Kabir",
        8.7
      ]
    ],
    "row_count": 3,
    "execution_time_ms": 12
  }
}
```

#### Validation Error Response (`422 Unprocessable Entity`)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "query"
      ],
      "msg": "Value error, Query cannot be empty or contain only whitespace.",
      "input": "   "
    }
  ]
}
```

### 2. `GET /health` — Service Health Check
Returns operational health status of the FastAPI backend.
```json
{
  "status": "healthy"
}
```

### 3. `GET /` — Root Welcome Endpoint
Returns service identification and status.
```json
{
  "message": "Welcome to QueryMind AI",
  "status": "Backend is running"
}
```

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

---

### Step 1: Clone Repository & Switch to Feature Branch

```bash
git clone https://github.com/pratyushsri1909/QueryMindAI.git
cd QueryMindAI
git checkout feature/application
```

---

### Step 2: Backend Setup & Execution

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv

   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1

   # On Linux / macOS:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the automated Pytest test suite:
   ```bash
   pytest -v
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The backend server is accessible at:
- **Base URL:** `http://localhost:8000/`
- **Health Check:** `http://localhost:8000/health`
- **Interactive OpenAPI (Swagger) Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Step 3: Frontend Setup & Execution

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. (Optional) Configure environment variable:
   ```bash
   cp .env.example .env
   # Default: VITE_API_BASE_URL=http://localhost:8000
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

The web client will be available at:
- **Local URL:** [http://localhost:5173/](http://localhost:5173/)

---

## 9. Mock Implementation Limitations & Disclaimers

The Day 2 implementation is designed specifically for full-stack integration and architectural validation. Please note the following constraints:

1. **No Live Database:** The SQL engine does **not** connect to PostgreSQL or execute arbitrary SQL queries against a live database. All row datasets are static fixture arrays designed to verify schema rendering and tabular display.
2. **Deterministic Mock NLP:** The NLP module uses deterministic pattern matching for demonstration queries (`students with CGPA`, `top students`, `courses`) and a general fallback for others. It does not employ statistical machine learning models or tokenizers.
3. **Execution Status:** Responses explicitly report execution status as `mock_success` to prevent ambiguity between mock results and production database execution.
