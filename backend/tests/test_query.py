"""Automated integration and unit tests for QueryMind AI query processing pipeline."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.nlp.mock_nlp import process_natural_language
from app.sql_engine.mock_sql_engine import process_ir

client = TestClient(app)


def test_post_query_success_cgpa() -> None:
    """Verify successful query processing for student CGPA query."""
    payload = {"query": "Show students with CGPA above 8.5"}
    response = client.post("/api/v1/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Query processed successfully"
    assert data["original_query"] == "Show students with CGPA above 8.5"
    assert data["intent"] == "FILTER"
    assert data["ir"]["table"] == "students"
    assert data["ir"]["conditions"][0]["column"] == "cgpa"
    assert data["ir"]["conditions"][0]["operator"] == ">"
    assert data["ir"]["conditions"][0]["value"] == 8.5
    assert data["generated_sql"] == "SELECT name, cgpa FROM students WHERE cgpa > 8.5;"
    assert data["execution"]["status"] == "mock_success"
    assert data["execution"]["columns"] == ["name", "cgpa"]
    assert len(data["execution"]["rows"]) == 3
    assert data["execution"]["row_count"] == 3
    assert data["execution"]["execution_time_ms"] == 12


def test_post_query_empty_string_rejected() -> None:
    """Verify that an empty string query is rejected with HTTP 422."""
    response = client.post("/api/v1/query", json={"query": ""})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_post_query_whitespace_only_rejected() -> None:
    """Verify that a whitespace-only query is rejected with HTTP 422."""
    response = client.post("/api/v1/query", json={"query": "    \t\n  "})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_post_query_missing_field_rejected() -> None:
    """Verify that missing 'query' key in request body returns HTTP 422."""
    response = client.post("/api/v1/query", json={})
    assert response.status_code == 422


def test_post_query_max_length_validation() -> None:
    """Verify that queries exceeding 500 characters are rejected with HTTP 422."""
    long_query = "show students " + ("a" * 500)
    response = client.post("/api/v1/query", json={"query": long_query})
    assert response.status_code == 422
    assert "500" in str(response.json())


def test_post_query_trims_whitespace() -> None:
    """Verify that leading and trailing whitespace is trimmed properly."""
    response = client.post(
        "/api/v1/query",
        json={"query": "   Show students with CGPA above 8.5   "},
    )
    assert response.status_code == 200
    assert response.json()["original_query"] == "Show students with CGPA above 8.5"


def test_response_schema_contract() -> None:
    """Verify that the response schema matches the exact team contract."""
    response = client.post(
        "/api/v1/query", json={"query": "Show students with CGPA above 8.5"}
    )
    assert response.status_code == 200
    data = response.json()

    # Top-level contract keys
    expected_top_keys = {
        "success",
        "message",
        "original_query",
        "intent",
        "ir",
        "generated_sql",
        "execution",
    }
    assert expected_top_keys.issubset(data.keys())

    # IR contract keys
    expected_ir_keys = {
        "intent",
        "table",
        "columns",
        "conditions",
        "order_by",
        "limit",
    }
    assert expected_ir_keys.issubset(data["ir"].keys())

    # Execution contract keys
    expected_exec_keys = {
        "status",
        "columns",
        "rows",
        "row_count",
        "execution_time_ms",
    }
    assert expected_exec_keys.issubset(data["execution"].keys())


def test_mock_nlp_module_directly() -> None:
    """Unit test for mock NLP module logic directly."""
    # Test CGPA query
    ir_cgpa = process_natural_language("Show students with CGPA above 8.5")
    assert ir_cgpa["intent"] == "FILTER"
    assert ir_cgpa["table"] == "students"
    assert ir_cgpa["columns"] == ["name", "cgpa"]
    assert ir_cgpa["conditions"][0]["value"] == 8.5

    # Test Sorting query
    ir_sort = process_natural_language("Show top students ordered by CGPA")
    assert ir_sort["intent"] == "SORT"
    assert ir_sort["order_by"] == "cgpa DESC"

    # Test Fallback query
    ir_fallback = process_natural_language("Some completely unrelated phrase")
    assert ir_fallback["intent"] == "SELECT_ALL"
    assert ir_fallback["table"] == "students"
    assert ir_fallback["limit"] == 10


def test_mock_sql_engine_directly() -> None:
    """Unit test for mock SQL engine logic directly."""
    ir = {
        "intent": "FILTER",
        "table": "students",
        "columns": ["name", "cgpa"],
        "conditions": [{"column": "cgpa", "operator": ">", "value": 8.5}],
        "order_by": None,
        "limit": None,
    }
    result = process_ir(ir)
    assert "SELECT name, cgpa FROM students WHERE cgpa > 8.5;" in result["generated_sql"]
    assert result["execution"]["status"] == "mock_success"
    assert result["execution"]["columns"] == ["name", "cgpa"]
    assert len(result["execution"]["rows"]) == 3
    assert result["execution"]["row_count"] == 3


def test_query_generic_fallback() -> None:
    """Verify that unknown query triggers deterministic fallback mock pipeline."""
    response = client.post(
        "/api/v1/query", json={"query": "Show general university details"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "SELECT_ALL"
    assert "SELECT id, name, department, cgpa FROM students" in data["generated_sql"]
    assert data["execution"]["status"] == "mock_success"
    assert data["execution"]["row_count"] == 5
