# Hierarchical Input Design (HID) — QueryMind AI

## 1. Overview and System Hierarchy

The Hierarchical Input Design (HID) outlines the functional decomposition of QueryMind AI. It models the architectural breakdown from high-level subsystems to granular operational submodules, detailing component responsibilities, dependency relationships, and team ownership.

```text
QueryMind AI
├── 1. User Interface (Frontend Subsystem)
│   ├── 1.1 Query Input Panel [Planned]
│   ├── 1.2 Submit & Execution Controls [Planned]
│   ├── 1.3 Query Status & Progress Visualizer [Planned]
│   ├── 1.4 Result Display & Table View [Planned]
│   └── 1.5 SQL Inspection & Explanation Panel [Planned]
├── 2. Backend API (FastAPI Gateway)
│   ├── 2.1 Service Lifecycle & Health Management [Implemented]
│   ├── 2.2 Request Ingestion & Data Validation [Planned]
│   ├── 2.3 API Routing & Controller Endpoints [Planned]
│   ├── 2.4 Error Handling & Global Exceptions [Planned]
│   └── 2.5 Security, CORS & Rate Limiting [Planned]
├── 3. NLP Engine — Member 1
│   ├── 3.1 Text Cleaning & Preprocessing [Planned]
│   ├── 3.2 Linguistic Tokenization & Lemmatization [Planned]
│   ├── 3.3 Intent Classification [Planned]
│   ├── 3.4 Named Entity Recognition (NER) & Attribute Extraction [Planned]
│   └── 3.5 Intermediate Representation (IR) Serialization [Planned]
├── 4. SQL Engine — Member 2
│   ├── 4.1 Relational Schema Catalog & Metadata Mapping [Planned]
│   ├── 4.2 SQL Dialect Query Synthesis [Planned]
│   ├── 4.3 Static SQL Validation & AST Parsing (SQLGlot) [Planned]
│   ├── 4.4 Read-Only Security Guardrails [Planned]
│   └── 4.5 Execution Pipeline & Result Formatting [Planned]
└── 5. Database & Schema Subsystem
    ├── 5.1 Students Entity Catalog [Planned]
    ├── 5.2 Courses Entity Catalog [Planned]
    ├── 5.3 Departments Entity Catalog [Planned]
    └── 5.4 Enrollments Entity Catalog [Planned]
```

---

## 2. Module Responsibilities and Status

### 2.1 User Interface (Frontend Subsystem)
- **Primary Responsibility:** Deliver a responsive, user-friendly graphical interface where academic stakeholders can input plain English queries, view real-time execution states, inspect generated SQL queries, and explore paginated database result tables.
- **Submodules:**
  - `Query Input Panel`: Natural language text input field with prompt recommendations and syntax helpers.
  - `Submit & Execution Controls`: Asynchronous event triggers for dispatching REST requests.
  - `Result Display & Table View`: Tabular presentation of database rows with sortable headers.
  - `SQL Inspection Panel`: Read-only code block highlighting the generated SQL query for complete transparency.
- **Status:** **Planned** (React + Vite single-page application in future development phases).

---

### 2.2 Backend API (FastAPI Application Gateway)
- **Primary Responsibility:** Serve as the central communication, validation, orchestration, and response-formatting layer connecting the client interface with the specialized backend processing engines.
- **Submodules:**
  - `Service Lifecycle & Health Management`: Provides core health monitoring (`/health`) and service metadata (`/`). [Implemented]
  - `Request Ingestion & Data Validation`: Validates schema conformance, data types, and bounds on incoming query payloads. [Planned]
  - `API Routing & Controller Endpoints`: Dispatches validated requests to pipeline handlers. [Planned]
  - `Response Handling`: Translates pipeline artifacts into standardized JSON responses or clean HTTP error envelopes. [Planned]
- **Status:** **Partially Implemented (Day 1)**:
  - Core FastAPI application framework initialized.
  - `GET /` and `GET /health` endpoints active and tested.
  - Clean modular architecture laid out in `app/`.
  - Comprehensive query processing endpoints (`/api/v1/query`) and request validation planned for subsequent iterations.

---

### 2.3 NLP Engine (Natural Language Processing)
- **Team Ownership:** **Member 1 (NLP Specialist)**
- **Primary Responsibility:** Transform raw, unstructured natural language questions into a structured, unambiguous Intermediate Representation (IR).
- **Submodules:**
  - `Text Preprocessing`: Lowercasing, noise removal, punctuation normalization.
  - `Tokenization & Lemmatization`: Breaking text into linguistic units and reducing words to root lemmas using NLTK and spaCy.
  - `Intent Classification`: Identifying analytical verbs (`SELECT`, `FILTER`, `COUNT`, `AGGREGATION`, `SORT`, `JOIN`) using Scikit-learn classification models.
  - `Entity Extraction`: Identifying database candidates (e.g., student names, department titles, metric bounds).
  - `Intermediate Representation Generation`: Serializing structured JSON capturing intent, tables, fields, and conditions.
- **Status:** **Planned** (To be developed by Member 1).

---

### 2.4 SQL Engine (SQL Generation & Validation)
- **Team Ownership:** **Member 2 (Database and SQL Engineer)**
- **Primary Responsibility:** Receive the structured Intermediate Representation from Member 1, map logical entities to the actual physical database schema, construct valid PostgreSQL queries, enforce read-only safety, and execute the query against the database.
- **Submodules:**
  - `Schema Mapping`: Resolves logical entity names to PostgreSQL tables and columns.
  - `SQL Generation`: Synthesizes syntactically correct ANSI/PostgreSQL queries.
  - `SQL Validation (SQLGlot)`: Parses the AST to verify query validity and strictly prohibits mutating operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`).
  - `Query Execution`: Uses SQLAlchemy / psycopg connections to run queries against PostgreSQL.
- **Status:** **Planned** (To be developed by Member 2).

---

### 2.5 Database & Target Academic Schema
- **Primary Responsibility:** Provide persistent relational storage with relational integrity, foreign keys, and indexes for query execution and benchmarking.
- **Core Entities:**
  - `students`: Records student ID, name, email, admission year, and CGPA.
  - `departments`: Records department ID, department name, building, and head of department.
  - `courses`: Records course code, title, credits, and offering department ID.
  - `enrollments`: Bridge table connecting students and courses with grades and semester.
- **Status:** **Planned** (PostgreSQL schema creation and seed data loading in future phases).

---

## 3. Inter-Module Dependency Graph

The operational flow between modules follows a clear sequential dependency model:

```text
[Frontend (Planned)]
        │ HTTP REST Request (JSON)
        ▼
[FastAPI Backend (Day 1 Implemented)]
        │ Normalized Payload
        ▼
[NLP Engine — Member 1 (Planned)]
        │ Structured Intermediate Representation (IR)
        ▼
[SQL Engine — Member 2 (Planned)]
        │ Parameterized SQL
        ▼
[PostgreSQL Database (Planned)]
```

---

## 4. Team Roles & Ownership Matrix

| Subsystem / Layer | Primary Owner | Day 1 Status | Future Deliverable |
| :--- | :--- | :--- | :--- |
| **Backend API & Orchestration** | Member 3 (Current Developer) | **Implemented Foundation** | Pipeline integration & endpoint routing |
| **Frontend UI (React/Vite)** | Member 3 (Current Developer) | **Planned** | Interactive web dashboard |
| **NLP Engine** | Member 1 | **Planned** | Intent classification & IR extraction |
| **SQL Engine & DB Execution**| Member 2 | **Planned** | Schema resolution, SQL generation & validation |
| **PostgreSQL Database** | Member 2 | **Planned** | Relational schemas, migrations, test datasets |
