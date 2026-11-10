# PostgreSQL Database Setup Guide — QueryMind AI (Day 3 Foundation)

This document provides complete, step-by-step setup, configuration, and verification instructions for the **QueryMind AI PostgreSQL Academic Database Foundation** on Windows.

---

## 1. Status & Prerequisites

| Component | Status | Details |
| :--- | :--- | :--- |
| **SQLAlchemy ORM Models** | **Implemented & Tested** | Provisional `students`, `courses`, `enrollments` schemas with constraints & indexes. |
| **Safe SQL Execution Service** | **Implemented & Tested** | SQLGlot AST inspection enforcing single read-only `SELECT` statements with credential masking. |
| **Idempotent Sample Seeder** | **Implemented & Tested** | `seed_database()` populates 5 students, 5 courses, and 9 enrollments idempotently. |
| **Connection Pooling & Sessions** | **Implemented & Tested** | Pre-ping pooling, session generator (`get_db`), and connection health check. |
| **Local PostgreSQL Server** | **Requires Local Setup** | PostgreSQL 18 is installed at `C:\Program Files\PostgreSQL\18`. Service requires starting and DB creation. |

---

## 2. Windows PostgreSQL Service Setup

PostgreSQL 18 binaries are located at:
```text
C:\Program Files\PostgreSQL\18\bin
```

### Step 2.1: Verify or Start PostgreSQL Windows Service

Open an elevated PowerShell (Run as Administrator) or use the Windows Services GUI (`services.msc`):

```powershell
# Check service status
Get-Service -Name *postgres*

# Start the PostgreSQL service if stopped
Start-Service -Name "postgresql-x64-18"
```

Alternatively, from an Administrator terminal using `pg_ctl`:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\18\data" start
```

Verify reachability:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_isready.exe"
# Expected output: localhost:5432 - accepting connections
```

---

## 3. Database Creation

Using `psql.exe` or `createdb.exe`, create the target database `querymind_db`:

```powershell
# Using createdb:
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -h localhost -p 5432 querymind_db

# Or connect interactively via psql:
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -p 5432
```

In the `psql` console:
```sql
CREATE DATABASE querymind_db;
\c querymind_db
\q
```

---

## 4. Environment Configuration (`backend/.env`)

In the `backend/` directory, create or edit `.env` using `.env.example` as a template:

```env
# Execution Mode: "mock" (default Day 2 mock pipeline) or "database" (PostgreSQL execution)
QUERYMIND_MODE=database

# PostgreSQL Connection URL (psycopg3 driver)
DATABASE_URL=postgresql+psycopg://postgres:your_password_here@localhost:5432/querymind_db

# Statement execution timeout in milliseconds
DB_STATEMENT_TIMEOUT_MS=5000
```

> **Security Note:** Never commit `.env` containing actual database passwords. `.env` is excluded by `.gitignore`.

---

## 5. Schema Initialization & Sample Data Seeding

Run the initialization and seed scripts inside the virtual environment:

```powershell
cd backend
.\venv\Scripts\Activate.ps1

# 1. Create tables (students, courses, enrollments)
python -m app.database.init_db

# 2. Seed realistic academic sample records
python -m app.database.seed
```

Output:
```text
Creating tables on postgresql+psycopg://postgres:***@localhost:5432/querymind_db...
Database tables initialized successfully.
Database seeded successfully: {'students': 5, 'courses': 5, 'enrollments': 9}
```

---

## 6. Provisional Academic Schema Overview

The provisional database topology represents a university academic management system:

### Table: `students`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | Integer | Primary Key, Autoincrement | Unique student ID |
| `name` | String(100) | NOT NULL | Full student name |
| `batch` | Integer | NOT NULL, Index | Graduation/cohort year (e.g. 2028) |
| `cgpa` | Float | NOT NULL, Index, Range [0.0, 10.0] | Cumulative GPA |
| `department` | String(50) | NOT NULL, Index | Department code (CSE, AI, ECE) |

### Table: `courses`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `course_id` | Integer | Primary Key, Autoincrement | Unique course ID |
| `course_name` | String(150) | NOT NULL | Official course title |
| `credits` | Integer | NOT NULL, Range [1, 10] | Course credit hours |
| `department` | String(50) | NOT NULL, Index | Department offering course |

### Table: `enrollments`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `enrollment_id`| Integer | Primary Key, Autoincrement | Unique enrollment ID |
| `student_id` | Integer | FK -> `students.student_id`, ON DELETE CASCADE | Enrolled student |
| `course_id` | Integer | FK -> `courses.course_id`, ON DELETE CASCADE | Course taken |
| `semester` | String(30) | NOT NULL, Index | Term (e.g. "Fall 2024") |
| `grade` | String(5) | NULLABLE | Letter grade (A, B+, A-) |

---

## 7. Execution Modes: Mock vs. Database

QueryMind AI supports dual execution modes:

1. **`QUERYMIND_MODE=mock` (Default):**
   - Employs deterministic mock NLP and mock SQL engine.
   - Guaranteed to work in standalone development without requiring PostgreSQL to be running.
   - Returned status is `mock_success`.

2. **`QUERYMIND_MODE=database`:**
   - Evaluates incoming queries, parses to SQL, verifies safety using SQLGlot AST inspection, and executes directly on PostgreSQL.
   - If PostgreSQL is disconnected, reports a graceful structured error message without crashing.
   - Returned status is `database_success`.

3. **Per-Request Override:**
   API callers can optionally pass `"execution_mode": "database"` or `"execution_mode": "mock"` in `POST /api/v1/query` to override the server default.

---

## 8. Verification & Health Probes

Verify the connection status using the API health endpoints:

```bash
# General health check
curl http://127.0.0.1:8000/health

# Health check including PostgreSQL status
curl http://127.0.0.1:8000/health?include_db=true
# Response: {"status":"healthy","database":"connected"}

# Dedicated API health endpoint
curl http://127.0.0.1:8000/api/v1/health
```

