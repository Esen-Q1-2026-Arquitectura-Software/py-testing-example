"""
Unit tests for the Calculator FastAPI backend.

Coverage:
  - GET  /             health check
  - POST /add          addition endpoint
  - POST /multiply     multiplication endpoint

Run with:
  uv run pytest be/test_main.py -v
  uv run pytest be/test_main.py -v --cov=be --cov-report=term-missing
"""

import pytest
from fastapi.testclient import TestClient

from be.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post_add(a, b):
    return client.post("/add", json={"a": a, "b": b})


def post_multiply(a, b):
    return client.post("/multiply", json={"a": a, "b": b})


# ===========================================================================
# Health check  GET /
# ===========================================================================

class TestHealthCheck:
    def test_status_code_is_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_response_is_json(self):
        response = client.get("/")
        assert response.headers["content-type"].startswith("application/json")

    def test_status_field_is_ok(self):
        data = client.get("/").json()
        assert data["status"] == "ok"

    def test_service_field_is_present(self):
        data = client.get("/").json()
        assert data["service"] == "Calculator API"

    def test_response_has_exactly_two_keys(self):
        data = client.get("/").json()
        assert set(data.keys()) == {"status", "service"}


# ===========================================================================
# POST /add
# ===========================================================================

class TestAddEndpoint:

    # --- Happy path: integers -----------------------------------------------

    def test_status_code_is_200(self):
        assert post_add(3, 5).status_code == 200

    def test_adds_two_positive_integers(self):
        assert post_add(3, 5).json()["result"] == 8.0

    def test_adds_large_integers(self):
        assert post_add(1_000_000, 2_000_000).json()["result"] == 3_000_000.0

    # --- Happy path: floats -------------------------------------------------

    def test_adds_two_positive_floats(self):
        result = post_add(1.5, 2.5).json()["result"]
        assert result == pytest.approx(4.0)

    def test_adds_floats_with_rounding(self):
        result = post_add(0.1, 0.2).json()["result"]
        assert result == pytest.approx(0.3, rel=1e-6)

    # --- Edge cases ---------------------------------------------------------

    def test_adds_zeros(self):
        assert post_add(0, 0).json()["result"] == 0.0

    def test_adds_zero_and_positive(self):
        assert post_add(0, 7).json()["result"] == 7.0

    def test_adds_positive_and_zero(self):
        assert post_add(7, 0).json()["result"] == 7.0

    def test_adds_negative_numbers(self):
        assert post_add(-3, -5).json()["result"] == -8.0

    def test_adds_mixed_sign(self):
        assert post_add(-10, 4).json()["result"] == -6.0

    def test_adds_inverse_numbers_yields_zero(self):
        assert post_add(42, -42).json()["result"] == 0.0

    # --- Response shape -----------------------------------------------------

    def test_response_contains_field_a(self):
        assert post_add(2, 3).json()["a"] == 2.0

    def test_response_contains_field_b(self):
        assert post_add(2, 3).json()["b"] == 3.0

    def test_response_contains_field_result(self):
        assert "result" in post_add(2, 3).json()

    def test_response_operation_is_addition(self):
        assert post_add(1, 1).json()["operation"] == "addition"

    def test_response_has_exactly_four_keys(self):
        assert set(post_add(1, 2).json().keys()) == {"a", "b", "result", "operation"}

    # --- Input echoing ------------------------------------------------------

    def test_echoes_a_in_response(self):
        assert post_add(99, 1).json()["a"] == 99.0

    def test_echoes_b_in_response(self):
        assert post_add(1, 88).json()["b"] == 88.0

    # --- Validation errors --------------------------------------------------

    def test_missing_field_a_returns_422(self):
        response = client.post("/add", json={"b": 5})
        assert response.status_code == 422

    def test_missing_field_b_returns_422(self):
        response = client.post("/add", json={"a": 5})
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post("/add", json={})
        assert response.status_code == 422

    def test_string_value_for_a_returns_422(self):
        response = client.post("/add", json={"a": "hello", "b": 5})
        assert response.status_code == 422

    def test_string_value_for_b_returns_422(self):
        response = client.post("/add", json={"a": 5, "b": "world"})
        assert response.status_code == 422

    def test_null_value_for_a_returns_422(self):
        response = client.post("/add", json={"a": None, "b": 5})
        assert response.status_code == 422

    # --- Parametrized correctness -------------------------------------------

    @pytest.mark.parametrize("a, b, expected", [
        (0, 0, 0),
        (1, 1, 2),
        (-1, -1, -2),
        (100, -50, 50),
        (3.14, 2.86, 6.0),
        (0.5, 0.5, 1.0),
        (-7, 7, 0),
        (1e6, 1e6, 2e6),
    ])
    def test_add_parametrized(self, a, b, expected):
        result = post_add(a, b).json()["result"]
        assert result == pytest.approx(expected, rel=1e-9)


# ===========================================================================
# POST /multiply
# ===========================================================================

class TestMultiplyEndpoint:

    # --- Happy path: integers -----------------------------------------------

    def test_status_code_is_200(self):
        assert post_multiply(3, 5).status_code == 200

    def test_multiplies_two_positive_integers(self):
        assert post_multiply(3, 5).json()["result"] == 15.0

    def test_multiplies_large_integers(self):
        assert post_multiply(1_000, 1_000).json()["result"] == 1_000_000.0

    # --- Happy path: floats -------------------------------------------------

    def test_multiplies_two_positive_floats(self):
        result = post_multiply(2.5, 4.0).json()["result"]
        assert result == pytest.approx(10.0)

    def test_multiplies_floats_with_precision(self):
        result = post_multiply(0.1, 0.1).json()["result"]
        assert result == pytest.approx(0.01, rel=1e-6)

    # --- Edge cases ---------------------------------------------------------

    def test_multiply_by_zero_a(self):
        assert post_multiply(0, 99).json()["result"] == 0.0

    def test_multiply_by_zero_b(self):
        assert post_multiply(99, 0).json()["result"] == 0.0

    def test_multiply_both_zeros(self):
        assert post_multiply(0, 0).json()["result"] == 0.0

    def test_multiply_by_one_identity(self):
        assert post_multiply(7, 1).json()["result"] == 7.0

    def test_multiply_negative_numbers_yields_positive(self):
        assert post_multiply(-3, -5).json()["result"] == 15.0

    def test_multiply_mixed_sign_yields_negative(self):
        assert post_multiply(-4, 3).json()["result"] == -12.0

    def test_multiply_commutativity(self):
        assert post_multiply(6, 7).json()["result"] == post_multiply(7, 6).json()["result"]

    # --- Response shape -----------------------------------------------------

    def test_response_contains_field_a(self):
        assert post_multiply(2, 3).json()["a"] == 2.0

    def test_response_contains_field_b(self):
        assert post_multiply(2, 3).json()["b"] == 3.0

    def test_response_contains_field_result(self):
        assert "result" in post_multiply(2, 3).json()

    def test_response_operation_is_multiplication(self):
        assert post_multiply(2, 3).json()["operation"] == "multiplication"

    def test_response_has_exactly_four_keys(self):
        assert set(post_multiply(2, 3).json().keys()) == {"a", "b", "result", "operation"}

    # --- Input echoing ------------------------------------------------------

    def test_echoes_a_in_response(self):
        assert post_multiply(9, 2).json()["a"] == 9.0

    def test_echoes_b_in_response(self):
        assert post_multiply(3, 8).json()["b"] == 8.0

    # --- Validation errors --------------------------------------------------

    def test_missing_field_a_returns_422(self):
        response = client.post("/multiply", json={"b": 5})
        assert response.status_code == 422

    def test_missing_field_b_returns_422(self):
        response = client.post("/multiply", json={"a": 5})
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post("/multiply", json={})
        assert response.status_code == 422

    def test_string_value_for_a_returns_422(self):
        response = client.post("/multiply", json={"a": "hello", "b": 5})
        assert response.status_code == 422

    def test_string_value_for_b_returns_422(self):
        response = client.post("/multiply", json={"a": 5, "b": "world"})
        assert response.status_code == 422

    def test_null_value_for_b_returns_422(self):
        response = client.post("/multiply", json={"a": 5, "b": None})
        assert response.status_code == 422

    # --- Parametrized correctness -------------------------------------------

    @pytest.mark.parametrize("a, b, expected", [
        (0, 0, 0),
        (1, 1, 1),
        (-1, -1, 1),
        (-1, 1, -1),
        (2, 3, 6),
        (10, -5, -50),
        (3.14, 2.0, 6.28),
        (0.5, 0.5, 0.25),
        (1e3, 1e3, 1e6),
    ])
    def test_multiply_parametrized(self, a, b, expected):
        result = post_multiply(a, b).json()["result"]
        assert result == pytest.approx(expected, rel=1e-9)
