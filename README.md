# QueryMind AI — Natural Language to SQL Query Assistant

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791.svg?logo=postgresql)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00.svg)](https://www.sqlalchemy.org/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646cff.svg?logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38bdf8.svg?logo=tailwindcss)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

QueryMind AI is an academic and enterprise-oriented Natural Language to SQL (NL-to-SQL) assistant. It allows non-technical stakeholders—such as university administrators, researchers, students, and business analysts—to query relational databases (PostgreSQL) using intuitive, plain English rather than manually composing complex SQL queries.

---

## 1. Project Objective

Relational databases store vast amounts of mission-critical information, yet accessing this data often requires specialized proficiency in SQL syntax, relational algebra, and physical schema topology. QueryMind AI eliminates this barrier by providing:

1. **Semantic Query Translation:** Translating natural-language questions into syntactically valid ANSI/PostgreSQL queries.
2. **Read-Only Safety & Guardrails:** Enforcing strict AST validation (SQLGlot) to guarantee data security and prevent unauthorized schema or data mutations.
3. **Transparent Execution:** Exposing generated SQL side-by-side with execution results to foster user trust and verification.
4. **Accessible Interface:** Presenting tabular results through an interactive web-based interface.

---

## 2. End-to-End Pipeline Architecture

QueryMind AI connects natural language to database execution through a modular five-stage processing pipeline:

```text
[ Natural Language Input ]
           ↓
[ FastAPI Backend (POST /api/v1/query) ]
           ↓
[ NLP Module / Mock NLP ] ──→ [ Intermediate Representation (IR) ]
                                          ↓
                              [ SQL Engine / Mock Engine ] ──→ [ Generated ANSI SQL ]
                                                                        ↓
                                                [ Safe Read-Only Execution Service ]
                                                ├── Mode: "mock"     → Deterministic Fixture Data
                                                └── Mode: "database" → PostgreSQL Execution
                                                                        ↓
                                                            [ React + Vite Web UI ]
```

> **Architecture & Independence Notice:**  
> - **Mock Mode (Default):** Preserves the functioning Day 2 prototype using deterministic mock NLP and SQL modules. It requires no live PostgreSQL server to run or test.
> - **Database Mode:** Utilizes the Day 3 PostgreSQL database foundation (`students`, `courses`, `enrollments`) with SQLGlot AST read-only enforcement. Real ML/NLP intent parsing will be completed by Member 1, and final SQL schema mapping will be finalized by Member 2.

---

## 3. Technology Stack

### Backend:
- **Language & Runtime:** Python 3.11
- **API Framework:** FastAPI & Uvicorn (ASGI)
- **Database & Driver:** PostgreSQL 18, SQLAlchemy 2.0, `psycopg` 3 (binary)
- **SQL Parsing & Security:** SQLGlot (AST parsing, read-only validation)
- **Configuration & Validation:** Pydantic v2, Python-dotenv
- **Testing:** Pytest, HTTPX (`fastapi.testclient.TestClient`)
- **Future ML/NLP Integration (Member 1):** NLTK, spaCy, Scikit-learn

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
| **Member 1** | **NLP Engine** | Preprocessing, tokenization, intent classification, entity extraction, and Intermediate Representation (IR) generation. *(Day 2: Mock NLP prototype)* |
| **Member 2** | **Database & SQL Engine** | Schema mapping catalog, SQL generation, SQLGlot AST validation, read-only security enforcement, and PostgreSQL execution. *(Day 2: Mock SQL synthesizer; Day 3: Foundation prepared)* |
| **Member 3 (Current)** | **Backend, Frontend & Integration** | FastAPI architecture, Pydantic contracts, PostgreSQL foundation, safe execution service, CORS configuration, automated test suites, React + Vite web dashboard. *(Day 1, Day 2 & Day 3 Completed)* |

---

## 5. System Design Documentation Index

Comprehensive engineering specifications are cataloged inside the [`docs/`](docs/) directory:

| Artifact | Document Description | Direct Link |
| :--- | :--- | :--- |
| **Database Setup** | **PostgreSQL Setup Guide** — Windows installation, service startup, DB creation, and seeding. | [Read Database Setup](docs/DATABASE_SETUP.md) |
| **LID** | **Logical Input Design** — Defines logical inputs, validation constraints, query types, and the IR contract. | [Read LID](docs/LID.md) |
| **HID** | **Hierarchical Input Design** — Decomposes the system into functional hierarchies, modules, dependencies, and team ownership. | [Read HID](docs/HID.md) |
| **Code File** | **Source Code Design** — Catalogs repository structure, package responsibilities, coding standards, and codebase snippets. | [Read Code File](docs/CODE_FILE.md) |
| **Flow File** | **System Workflow** — Step-by-step pipeline from natural language input to tabular display. | [Read Flow File](docs/FLOW_FILE.md) |
| **Decision File** | **Decision Logic** — Defines business rules, decision tables, error trees, and pseudocode. | [Read Decision File](docs/DECISION_FILE.md) |

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
- [x] Modern light-theme React + Vite web dashboard (`frontend/`).

### Day 3 Deliverables (Completed):
- [x] PostgreSQL database configuration with environment-based settings and `.env.example` template.
- [x] Modern SQLAlchemy 2.0 ORM models for provisional academic schema (`students`, `courses`, `enrollments`).
- [x] Connection pooling with pre-ping validation, session generator (`get_db`), and connection health checking.
- [x] Safe SQL Execution Service (`app.services.database_service`):
  - SQLGlot AST inspection enforcing single read-only `SELECT` statements.
  - Strict rejection of mutations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`).
  - Protection against sensitive system catalog access (`pg_shadow`, `pg_authid`).
  - Credential masking in error responses.
- [x] Idempotent sample data seeder (`app.database.seed`) populating 5 students, 5 courses, and 9 enrollments.
- [x] Schema initializer script (`app.database.init_db`).
- [x] Dual execution mode support (`QUERYMIND_MODE=mock` vs `QUERYMIND_MODE=database`).
- [x] Health check database status reporting (`/health?include_db=true` and `/api/v1/health`).
- [x] 37 automated backend tests passing across all three days (`pytest -v`).
- [x] Direct PostgreSQL inspection endpoints (`/api/v1/database/health`, `/database/students`, `/database/courses`, `/database/enrollments`).

### Planned (Future Iterations):
- [ ] Member 1: Real spaCy/NLTK pipeline and machine learning intent classifier.
- [ ] Member 2: Final SQL schema mapping catalog and PostgreSQL AST translation.

---

## 7. API Endpoint Documentation

### Base URL
`http://localhost:8000`

### 1. `POST /api/v1/query` — Process Natural Language Query
Transforms a natural language string into ANSI/PostgreSQL via the pipeline and executes via mock or PostgreSQL mode.

#### Request Payload
```json
{
  "query": "Show students with CGPA above 8.5",
  "execution_mode": "mock"
}
```
*Note: `execution_mode` is optional ("mock" or "database"). Defaults to `QUERYMIND_MODE` from configuration.*

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
    "columns": ["name", "cgpa"],
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
    "columns": ["name", "cgpa"],
    "rows": [
      ["Aarav", 9.1],
      ["Diya", 8.8],
      ["Kabir", 8.7]
    ],
    "row_count": 3,
    "execution_time_ms": 12
  }
}
```

### 2. `GET /health` — Service Health Check
- `GET /health` returns `{"status": "healthy"}` (backward-compatible).
- `GET /health?include_db=true` returns `{"status": "healthy", "database": "connected"}`.

### 3. `GET /api/v1/health` — Dedicated API & Database Health Check
Returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "dialect": "postgresql"
}
```

### 4. `GET /api/v1/database/health` — Direct PostgreSQL Connection Health Check
Executes a lightweight `SELECT 1` ping using SQLAlchemy against the live PostgreSQL database. Returns HTTP 503 if unavailable.

#### Success Response (`200 OK`)
```json
{
  "status": "connected",
  "database": "querymind_db",
  "database_type": "postgresql"
}
```

### 5. `GET /api/v1/database/students` — Retrieve Seeded Students
Fetches actual student records directly from PostgreSQL via SQLAlchemy ORM.

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "source": "postgresql",
  "count": 5,
  "data": [
    {
      "student_id": 1,
      "id": 1,
      "name": "Aarav Sharma",
      "batch": 2024,
      "cgpa": 9.1,
      "department": "CSE"
    },
    {
      "student_id": 2,
      "id": 2,
      "name": "Diya Patel",
      "batch": 2024,
      "cgpa": 8.8,
      "department": "AI"
    },
    {
      "student_id": 3,
      "id": 3,
      "name": "Kabir Verma",
      "batch": 2025,
      "cgpa": 8.7,
      "department": "CSE"
    },
    {
      "student_id": 4,
      "id": 4,
      "name": "Meera Nair",
      "batch": 2025,
      "cgpa": 8.2,
      "department": "AI"
    },
    {
      "student_id": 5,
      "id": 5,
      "name": "Rohan Gupta",
      "batch": 2024,
      "cgpa": 7.9,
      "department": "ECE"
    }
  ]
}
```

### 6. `GET /api/v1/database/courses` — Retrieve Seeded Courses
Fetches actual course records directly from PostgreSQL via SQLAlchemy ORM.

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "source": "postgresql",
  "count": 5,
  "data": [
    {
      "course_id": 101,
      "id": 101,
      "course_name": "Database Management Systems",
      "credits": 4,
      "department": "CSE"
    },
    {
      "course_id": 102,
      "id": 102,
      "course_name": "Natural Language Processing",
      "credits": 3,
      "department": "AI"
    },
    {
      "course_id": 103,
      "id": 103,
      "course_name": "Data Structures & Algorithms",
      "credits": 4,
      "department": "CSE"
    },
    {
      "course_id": 104,
      "id": 104,
      "course_name": "Machine Learning",
      "credits": 3,
      "department": "AI"
    },
    {
      "course_id": 105,
      "id": 105,
      "course_name": "Digital Signal Processing",
      "credits": 3,
      "department": "ECE"
    }
  ]
}
```

### 7. `GET /api/v1/database/enrollments` — Retrieve Seeded Enrollments
Fetches actual enrollment records directly from PostgreSQL with joined student and course relations.

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "source": "postgresql",
  "count": 9,
  "data": [
    {
      "enrollment_id": 1,
      "id": 1,
      "student_id": 1,
      "course_id": 101,
      "semester": "Fall 2024",
      "grade": "A",
      "student_name": "Aarav Sharma",
      "course_name": "Database Management Systems"
    }
  ]
}
```

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 18 (for database mode)
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

4. Configure environment variables (Optional):
   ```bash
   cp .env.example .env
   # Default: QUERYMIND_MODE=mock
   # Set QUERYMIND_MODE=database to enable PostgreSQL execution
   ```

5. Run all automated Pytest tests:
   ```bash
   pytest -v
   ```

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

### Step 3: PostgreSQL Database Setup (Optional for Database Mode)

To set up the local PostgreSQL database:

```powershell
# 1. Start PostgreSQL 18 service (Windows PowerShell as Admin)
Start-Service -Name "postgresql-x64-18"

# 2. Create the target database
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -h localhost -p 5432 querymind_db

# 3. Create tables and seed sample academic data
python -m app.database.init_db
python -m app.database.seed
```

See [`docs/DATABASE_SETUP.md`](docs/DATABASE_SETUP.md) for detailed configuration options.

---

### Step 4: Frontend Setup & Execution

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

The web dashboard is accessible at:
- **Local URL:** [http://localhost:5173/](http://localhost:5173/)

---

## 9. Mock Mode vs. Database Mode

| Feature | Mock Mode (`QUERYMIND_MODE=mock`) | Database Mode (`QUERYMIND_MODE=database`) |
| :--- | :--- | :--- |
| **Prerequisites** | None (Runs offline) | PostgreSQL running with `querymind_db` |
| **Execution** | Deterministic static fixture data | Live query execution via SQLAlchemy |
| **AST Security** | N/A | SQLGlot AST inspection enforcing single read-only `SELECT` |
| **Response Status** | `mock_success` | `database_success` (or `error` if offline) |
| **Use Case** | Day 2 UI verification, frontend prototyping | Live database querying & verification |
