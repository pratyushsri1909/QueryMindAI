# QueryMind AI — Natural Language to SQL Query Assistant

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
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

## 2. Example Query Transformation

### Natural Language Input:
> *"Show students whose CGPA is greater than 8.5."*

### Translated SQL Query:
```sql
SELECT *
FROM students
WHERE cgpa > 8.5;
```

### Result Schema:
| student_id | first_name | last_name | department_id | cgpa | graduation_year |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `STU-1042` | Elena | Vance | `DEPT-CS` | 8.92 | 2025 |
| `STU-1089` | Marcus | Chen | `DEPT-EE` | 8.65 | 2024 |
| `STU-1120` | Sophia | Patel | `DEPT-CS` | 9.10 | 2025 |

---

## 3. Technology Stack

- **Backend Framework:** FastAPI & Uvicorn (ASGI)
- **Database & ORM:** PostgreSQL, SQLAlchemy, `psycopg` (binary)
- **NLP & Linguistics:** NLTK, spaCy
- **Machine Learning:** Scikit-learn (Intent Classification)
- **Data & Parsing:** Pandas, SQLGlot (SQL AST Validation)
- **Testing:** Pytest, HTTPX (`fastapi.testclient`)
- **Frontend (Future Phase):** React + Vite

---

## 4. Team Architecture & Responsibilities

QueryMind AI is collaboratively developed by a three-member engineering team with clear boundaries of concern:

| Team Member | Domain Responsibility | Current Deliverables & Scope |
| :--- | :--- | :--- |
| **Member 1** | **NLP Engine** | Text preprocessing, tokenization, intent classification, entity extraction, and Intermediate Representation (IR) generation. *(Planned)* |
| **Member 2** | **Database & SQL Engine** | Schema mapping catalog, SQL generation, SQLGlot AST validation, read-only security enforcement, and PostgreSQL execution. *(Planned)* |
| **Member 3 (Current)** | **Backend, Frontend & Integration** | GitHub workflow setup, FastAPI application architecture, REST API endpoints, automated test suites, system design documentation, and future React UI. *(Day 1 Implemented)* |

---

## 5. System Design Documentation Index

Comprehensive engineering specifications are cataloged inside the [`docs/`](docs/) directory:

| Artifact | Document Description | Direct Link |
| :--- | :--- | :--- |
| **LID** | **Logical Input Design** — Defines logical inputs, validation constraints, query types, and the NLP-to-SQL Intermediate Representation contract. | [Read LID](docs/LID.md) |
| **HID** | **Hierarchical Input Design** — Decomposes the system into functional hierarchies, modules, dependencies, and team ownership. | [Read HID](docs/HID.md) |
| **Code File** | **Source Code Design** — Catalogs repository structure, package responsibilities, coding standards, and existing codebase snippets. | [Read Code File](docs/CODE_FILE.md) |
| **Flow File** | **System Workflow** — Step-by-step pipeline from natural language input to tabular display, accompanied by a GitHub Mermaid diagram. | [Read Flow File](docs/FLOW_FILE.md) |
| **Decision File** | **Decision Logic** — Defines business rules, decision tables, error trees, and pseudocode across all five processing stages. | [Read Decision File](docs/DECISION_FILE.md) |

---

## 6. Current Implementation Status (Day 1)

- [x] Git branch workflow isolated on `feature/application`.
- [x] Modular project directory structure initialized (`backend/`, `frontend/`, `datasets/`, `docs/`).
- [x] Python 3.11 virtual environment and dependency specifications (`backend/requirements.txt`).
- [x] FastAPI application initialized with metadata and OpenAPI/Swagger support (`backend/app/main.py`).
- [x] Root endpoint (`GET /`) and Health Check endpoint (`GET /health`) implemented.
- [x] Automated test suite with Pytest and FastAPI TestClient (`backend/tests/test_main.py`).
- [x] Complete system design documentation (LID, HID, Code File, Flow File, Decision File).
- [ ] *(Planned)* Member 1 NLP Engine integration.
- [ ] *(Planned)* Member 2 SQL Engine & PostgreSQL execution pipeline.
- [ ] *(Planned)* Member 3 React + Vite web dashboard.

---

## 7. Installation & Setup Instructions

### Prerequisites
- Python 3.11+
- Git

### 1. Clone Repository & Switch to Feature Branch
```bash
git clone https://github.com/pratyushsri1909/QueryMindAI.git
cd QueryMindAI
git checkout feature/application
```

### 2. Set Up Virtual Environment (Inside `backend/`)
```bash
cd backend
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 8. Running the Backend Server

Start the local development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

Once running, the service is accessible at:
- **Base URL:** `http://127.0.0.1:8000/`
- **Health Check:** `http://127.0.0.1:8000/health`
- **Interactive OpenAPI (Swagger) Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Docs (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 9. Running Automated Tests

Run the test suite using `pytest`:

```bash
cd backend
pytest -v
```

All tests verify endpoint availability, response status codes, and exact JSON payload contracts.
