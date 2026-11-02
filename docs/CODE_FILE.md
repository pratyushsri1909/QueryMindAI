# Source Code Design (CODE_FILE) — QueryMind AI

## 1. Project Directory Structure

The repository follows a clean, modular structure designed to support collaborative multi-engineer development, clear division of concerns, and isolated dependency management:

```text
QueryMindAI/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App package indicator
│   │   ├── api/                 # API controllers and routing [Implemented - Day 2]
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── core/                # Core configuration and settings [Implemented - Day 2]
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   ├── database/            # SQLAlchemy database engine and session [Planned]
│   │   │   └── __init__.py
│   │   ├── models/              # Database ORM models [Planned]
│   │   │   └── __init__.py
│   │   ├── schemas/             # Pydantic request/response schemas [Implemented - Day 2]
│   │   │   ├── __init__.py
│   │   │   └── query.py
│   │   ├── nlp/                 # NLP Engine by Member 1 [Mock Implemented - Day 2]
│   │   │   ├── __init__.py
│   │   │   └── mock_nlp.py
│   │   ├── sql_engine/          # SQL Engine by Member 2 [Mock Implemented - Day 2]
│   │   │   ├── __init__.py
│   │   │   └── mock_sql_engine.py
│   │   └── main.py              # Application entrypoint & base endpoints [Implemented]
│   ├── tests/
│   │   ├── __init__.py          # Test suite package indicator
│   │   ├── test_main.py         # Pytest automated API tests [Implemented]
│   │   └── test_query.py        # Pytest pipeline and validation tests [Implemented - Day 2]
│   ├── requirements.txt         # Backend Python dependencies [Implemented]
│   └── venv/                    # Isolated Python virtual environment (ignored)
├── frontend/                    # React + Vite web client [Implemented - Day 2]
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── QueryInput.jsx
│   │   │   ├── SqlPanel.jsx
│   │   │   ├── ResultsTable.jsx
│   │   │   └── ExecutionInfo.jsx
│   │   ├── services/
│   │   │   └── queryService.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── datasets/
│   └── .gitkeep                 # Sample benchmark datasets and schemas [Planned]
├── docs/
│   ├── LID.md                   # Logical Input Design [Implemented]
│   ├── HID.md                   # Hierarchical Input Design [Implemented]
│   ├── CODE_FILE.md             # Source Code Design [Implemented]
│   ├── FLOW_FILE.md             # System Workflow [Implemented]
│   └── DECISION_FILE.md         # Decision Logic Design [Implemented]
├── .gitignore                   # Git exclusion rules [Implemented]
└── README.md                    # Project documentation [Implemented]
```

---

## 2. Purpose of Important Source Files

### 2.1 Implemented Files (Day 1)

- **`backend/app/main.py`**:
  The central FastAPI application instantiation file. It defines the core application metadata, configures OpenAPI documentation, and hosts the root welcome and health check endpoints.

- **`backend/tests/test_main.py`**:
  The automated test file using `pytest` and `fastapi.testclient.TestClient`. It provides deterministic verification of HTTP status codes and response bodies for the core application endpoints.

- **`backend/requirements.txt`**:
  Specifies the unpinned top-level Python packages required across all backend layers (FastAPI, SQLAlchemy, psycopg, spaCy, NLTK, Scikit-learn, SQLGlot, Pytest, HTTPX).

- **`.gitignore`**:
  Guarantees repository hygiene by excluding Python caches (`__pycache__`), virtual environments (`venv/`), environment variables (`.env`), test artifacts (`.pytest_cache/`), and IDE configurations (`.vscode/`, `.idea/`).

---

## 3. Responsibilities of Backend Packages

### 3.1 `backend/app/core/`
- **Responsibility:** Holds application-wide configurations, environment variable loaders (using `pydantic-settings` or `python-dotenv`), security configurations (CORS headers, secret keys), and logging setups.
- **Status:** Package initialized; detailed configuration logic **Planned**.

### 3.2 `backend/app/api/`
- **Responsibility:** Modular API routers (e.g., `api/v1/query.py`, `api/v1/history.py`, `api/v1/schema.py`) to keep route handlers decoupled from `main.py`.
- **Status:** Package initialized; query routes **Planned**.

### 3.3 `backend/app/schemas/`
- **Responsibility:** Pydantic models defining strict validation schemas for incoming request bodies, query parameters, Intermediate Representation (IR) structures, and outgoing JSON responses.
- **Status:** Package initialized; model schemas **Planned**.

### 3.4 `backend/app/models/`
- **Responsibility:** SQLAlchemy ORM model declarations mapping to database tables (`Student`, `Course`, `Department`, `Enrollment`).
- **Status:** Package initialized; ORM mapping **Planned**.

### 3.5 `backend/app/database/`
- **Responsibility:** SQLAlchemy database engine configuration, sessionmaker factories, and dependency-injected session yields (`get_db`).
- **Status:** Package initialized; connection pools **Planned**.

### 3.6 `backend/app/nlp/` (Owned by Member 1)
- **Responsibility:** Housing NLP models, tokenizers, lemmatizers, intent classification pipelines, and entity extraction logic to convert raw text into structured Intermediate Representation.
- **Status:** Package initialized; NLP models **Planned**.

### 3.7 `backend/app/sql_engine/` (Owned by Member 2)
- **Responsibility:** Translating the Intermediate Representation into validated, dialect-specific PostgreSQL queries, running SQLGlot AST validation, and executing queries securely.
- **Status:** Package initialized; SQL compiler **Planned**.

---

## 4. Current Implementation Code Snippets

### 4.1 FastAPI Application (`backend/app/main.py`)

```python
"""Main entry point for the QueryMind AI FastAPI backend application."""

from typing import Dict
from fastapi import FastAPI, status

app = FastAPI(
    title="QueryMind AI",
    description="Natural Language to SQL Query Assistant",
    version="1.0.0",
)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root Welcome Endpoint",
    response_model=Dict[str, str],
)
def read_root() -> Dict[str, str]:
    """Root endpoint returning service identification and running status."""
    return {
        "message": "Welcome to QueryMind AI",
        "status": "Backend is running",
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check Endpoint",
    response_model=Dict[str, str],
)
def health_check() -> Dict[str, str]:
    """Health check endpoint indicating whether the backend service is operational."""
    return {
        "status": "healthy",
    }
```

### 4.2 Automated Test Implementation (`backend/tests/test_main.py`)

```python
"""Automated tests for QueryMind AI core FastAPI endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_status_code() -> None:
    """Verify that GET / returns HTTP 200 status code."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_welcome_message() -> None:
    """Verify that GET / returns the expected welcome message and payload."""
    response = client.get("/")
    assert response.json() == {
        "message": "Welcome to QueryMind AI",
        "status": "Backend is running",
    }


def test_health_status_code() -> None:
    """Verify that GET /health returns HTTP 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_payload() -> None:
    """Verify that GET /health returns exactly {'status': 'healthy'}."""
    response = client.get("/health")
    assert response.json() == {"status": "healthy"}
```

---

## 5. Dependencies and Requirements

The declared dependencies in `backend/requirements.txt` are unpinned top-level packages covering the full lifecycle of QueryMind AI:

| Package | Purpose |
| :--- | :--- |
| `fastapi` | High-performance asynchronous web framework |
| `uvicorn[standard]` | ASGI web server for running the FastAPI application |
| `sqlalchemy` | SQL toolkit and Object Relational Mapper (ORM) |
| `psycopg[binary]` | PostgreSQL database adapter for Python |
| `python-dotenv` | Reads key-value pairs from `.env` files for configuration |
| `pydantic` | Data validation and settings management using Python type annotations |
| `nltk` | Natural Language Toolkit for linguistic processing and tokenization |
| `spacy` | Industrial-strength NLP library for entity recognition and parsing |
| `scikit-learn` | Machine learning toolkit for intent classification |
| `pandas` | Tabular data analysis and structured result formatting |
| `sqlglot` | SQL parser, transpiler, and Abstract Syntax Tree (AST) validator |
| `pytest` | Testing framework for unit and integration testing |
| `httpx` | Asynchronous HTTP client required by FastAPI `TestClient` |

---

## 6. Coding Standards & Guidelines

- **PEP 8 Conformance:** All code adheres strictly to PEP 8 styling conventions.
- **Type Annotations:** All functions, methods, and endpoint signatures must have full Python type hints (`typing.Dict`, `typing.List`, `typing.Optional`, etc.).
- **Docstrings:** Standard Python docstrings describing behavior, arguments, and return types on all modules, classes, and functions.
- **Error Handling:** Avoid generic exceptions; use explicit FastAPI `HTTPException` with appropriate HTTP status codes.
- **Security:** Strict separation of credentials via `.env`; no plaintext secrets committed to version control.

---

## 7. Testing Architecture

- Tests reside in `backend/tests/` and mirror the package structure of `backend/app/`.
- Test execution is executed via `pytest -v` from the `backend/` directory.
- Fast, non-networked testing of endpoints is achieved using `fastapi.testclient.TestClient`.
- Future tests will include mock tests for Member 1's NLP models and Member 2's SQL generation engine without requiring a live PostgreSQL instance.

---

## 8. Planned Future Source Files

| Planned Path | Anticipated Owner | Description |
| :--- | :--- | :--- |
| `backend/app/core/config.py` | Member 3 | Environment-based application settings |
| `backend/app/api/v1/endpoints/query.py` | Member 3 | Main REST endpoint orchestrating NL-to-SQL |
| `backend/app/schemas/query.py` | Member 3 | Pydantic schemas for query requests and responses |
| `backend/app/nlp/preprocessor.py` | Member 1 | Text normalization and cleaning routines |
| `backend/app/nlp/classifier.py` | Member 1 | Intent classification model and inference |
| `backend/app/nlp/extractor.py` | Member 1 | Entity, attribute, and value extraction |
| `backend/app/sql_engine/generator.py` | Member 2 | Intermediate Representation to SQL converter |
| `backend/app/sql_engine/validator.py` | Member 2 | AST and security validator using SQLGlot |
| `backend/app/database/session.py` | Member 2 / 3 | SQLAlchemy connection pooling and session lifecycle |
| `frontend/src/App.jsx` | Member 3 | React application root interface |
