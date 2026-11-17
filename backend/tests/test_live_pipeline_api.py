"""Regression tests for the real NLP -> SQL -> database API path."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_database_mode_uses_real_nlp_sql_and_bound_parameters(monkeypatch):
    captured = {}

    def fake_execute_read_query(sql, *, params=None):
        captured["sql"] = sql
        captured["params"] = params
        return {
            "status": "database_success",
            "columns": ["name", "cgpa"],
            "rows": [["Aarav Sharma", 9.1]],
            "row_count": 1,
            "execution_time_ms": 2,
            "error": None,
        }

    monkeypatch.setattr(
        "app.api.routes.execute_read_query",
        fake_execute_read_query,
    )

    response = client.post(
        "/api/v1/query",
        json={
            "query": "Show students with CGPA above 8.5",
            "execution_mode": "database",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True
    assert "students.cgpa > :p0" in payload["generated_sql"]
    assert payload["params"] == {"p0": 8.5}
    assert captured["sql"] == payload["generated_sql"]
    assert captured["params"] == {"p0": 8.5}
    assert payload["execution"]["status"] == "database_success"


def test_database_mode_returns_structured_error_for_unknown_domain():
    response = client.post("/api/v1/query", json={
        "query": "Show all rockets launched into orbit",
        "execution_mode": "database",
    })
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "ENTITY_NOT_FOUND"
    assert detail["message"]


def test_mock_mode_preserved():
    response = client.post("/api/v1/query", json={
        "query": "Show students with CGPA above 8.5",
        "execution_mode": "mock",
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["execution"]["status"] == "mock_success"
    assert "SELECT name, cgpa FROM students WHERE cgpa > 8.5;" == payload["generated_sql"]
