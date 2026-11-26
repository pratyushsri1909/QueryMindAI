# QueryMind AI — Natural Language to SQL Query Assistant

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![FastAPI](https://img.shields.io/badge/FastAPI-web%20API-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791.svg?logo=postgresql)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d71f00.svg)](https://www.sqlalchemy.org/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646cff.svg?logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38bdf8.svg?logo=tailwindcss)](https://tailwindcss.com/)

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
> - **Database Mode:** Uses the current rule-based NLP processor and parameterized SQL engine, followed by SQLGlot read-only validation and PostgreSQL execution. The current NLP implementation is rule-based; do not describe it as a trained ML model or LLM.

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
| **Member 1** | **NLP Engine** | Rule-based preprocessing, tokenization, lemmatization, intent classification, entity extraction, and canonical Intermediate Representation (IR) generation. |
| **Member 2** | **Database & SQL Engine** | Approved-schema mapping, parameterized SQL generation, SQL-engine IR validation, and read-only PostgreSQL execution through the shared database service. |
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
- [x] Backend unit, security, and integration tests are maintained under `backend/tests/` and the root NLP test module; CI runs them on pushes and pull requests.
- [x] Direct PostgreSQL inspection endpoints (`/api/v1/database/health`, `/database/students`, `/database/courses`, `/database/enrollments`).

### Remaining Release Decisions:
- [ ] Confirm whether a dedicated `departments` table is required. The original team plan lists it, but the current ORM, NLP schema, and SQL allowlist contain only `students`, `courses`, and `enrollments`, with department stored as a text column.
- [ ] Configure production PostgreSQL credentials and the deployed frontend origin before enabling `QUERYMIND_MODE=database`.
- [ ] Select hosting providers and configure deployment secrets outside the repository.
- [ ] Agree on a repository license with all contributors before adding a license file.

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
    "joins": [],
    "aggregations": [],
    "group_by": [],
    "order_by": null,
    "limit": null
  },
  "generated_sql": "SELECT name, cgpa FROM students WHERE cgpa > 8.5;",
  "params": {},
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

### Step 1: Clone the Current Release Branch

```bash
git clone https://github.com/pratyushsri1909/QueryMindAI.git
cd QueryMindAI
git checkout main
```

Use `main` for the integrated release. The `feature/application` branch is behind `main` and does not contain the latest SQL-engine changes.

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

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   **Key Configuration Settings:**
   - `QUERYMIND_MODE`: `mock` (default for offline demo) or `database` (real NLP $\rightarrow$ SQL $\rightarrow$ PostgreSQL pipeline).
   - `DATABASE_URL`: Connection string (`postgresql+psycopg://<user>:<password>@localhost:5432/querymind_db`).
   - `CORS_ORIGINS`: Comma-separated allowed frontend origins (e.g. `http://localhost:5173`).
   - `TEST_DATABASE_URL`: Mandatory connection string for live PostgreSQL integration tests (`test_postgres_integration.py`). Target database name **must** contain `test` (e.g. `postgresql+psycopg://postgres:password@localhost:5432/querymind_test_db`). Integration tests **never** fall back to `DATABASE_URL` to prevent accidental destruction of application data.

5. Run automated tests:
   ```bash
   # Run all backend unit, security, and integration tests:
   pytest -v backend/tests test_nlp_engine.py

   # Run live PostgreSQL integration tests (requires dedicated test database):
   # 1. Create test database: createdb -U postgres -h localhost -p 5432 querymind_test_db
   # 2. Set environment variable: export TEST_DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5432/querymind_test_db"
   # 3. Execute:
   pytest -v backend/tests/test_postgres_integration.py
   ```

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

### Step 3: PostgreSQL Database Setup & Least-Privilege Role

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

#### Production Least-Privilege Application Role
**Important Security Requirement:** In production environments, QueryMind AI must **never** run under a PostgreSQL superuser account. Instead, configure a dedicated application role (`querymind_app`) granted strictly `SELECT` permissions on `students`, `courses`, and `enrollments`, with all mutation privileges revoked and `default_transaction_read_only = on`.

To create the restricted application role, execute the provided setup script as database administrator:
```bash
psql -U postgres -d querymind_db -f scripts/setup_restricted_role.sql
```
Then update `DATABASE_URL` in your production environment settings:
```env
DATABASE_URL=postgresql+psycopg://querymind_app:YOUR_SECURE_PASSWORD@localhost:5432/querymind_db
```

See [`docs/DATABASE_SETUP.md`](docs/DATABASE_SETUP.md) for detailed configuration options.

---

### Step 4: Frontend Setup & Execution

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   npm ci
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

---

## 10. Production Deployment Checklist

The repository does not currently include provider-specific deployment manifests. Before public deployment:

1. Provision PostgreSQL and set `QUERYMIND_MODE=database`.
2. Set `DATABASE_URL` in the backend host's secret/environment settings. Never commit `.env` or database credentials.
3. Set `CORS_ORIGINS` to the exact frontend origin(s), comma-separated. Do not use `*` with credentialed CORS.
4. Run `python -m app.database.init_db` and `python -m app.database.seed` from `backend/` as a controlled database setup step.
5. Deploy the backend as an ASGI service from `backend/`, using `uvicorn app.main:app --host 0.0.0.0 --port <host-port>`.
6. Set frontend build variable `VITE_API_BASE_URL` to the deployed backend URL, then run `npm ci` and `npm run build` from `frontend/` and publish the generated `dist/` directory.
7. Verify health endpoints, filtered queries, aggregate queries, JOIN queries, empty results, and rejected out-of-domain queries against the deployed service.

The current NLP implementation is rule-based. Do not describe it as a trained machine-learning model or LLM-powered system unless that capability is added and evaluated.
