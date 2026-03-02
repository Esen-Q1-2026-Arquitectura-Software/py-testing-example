"""
Basic unit tests for the Flask frontend (fe/app.py).

The FastAPI backend is mocked — no running server required.

Run with:
  uv run pytest fe/test_app.py -v
"""

import sys
import os
from unittest.mock import patch

import pytest

# Make the fe package importable when running from the project root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fe.app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helper: a fake call_backend that returns a realistic API response
# ---------------------------------------------------------------------------

def fake_backend(operation: str, result: float, a: float, b: float) -> dict:
    return {
        "a": a,
        "b": b,
        "result": result,
        "operation": "addition" if operation == "add" else "multiplication",
    }


# ===========================================================================
# GET /  — index page
# ===========================================================================

class TestIndexPage:
    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_form(self, client):
        html = client.get("/").data.decode()
        assert "<form" in html


# ===========================================================================
# POST /calculate  — addition
# ===========================================================================

class TestAddition:
    def test_add_integers_returns_200(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("add", 8.0, 3.0, 5.0)):
            response = client.post("/calculate", data={"operation": "add", "a": "3", "b": "5"})
        assert response.status_code == 200

    def test_add_integers_shows_result(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("add", 8.0, 3.0, 5.0)):
            html = client.post("/calculate", data={"operation": "add", "a": "3", "b": "5"}).data.decode()
        assert "8.0" in html

    def test_add_floats_returns_200(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("add", 3.5, 1.5, 2.0)):
            response = client.post("/calculate", data={"operation": "add", "a": "1.5", "b": "2.0"})
        assert response.status_code == 200

    def test_add_floats_shows_result(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("add", 3.5, 1.5, 2.0)):
            html = client.post("/calculate", data={"operation": "add", "a": "1.5", "b": "2.0"}).data.decode()
        assert "3.5" in html

    def test_add_shows_addition_label(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("add", 5.0, 2.0, 3.0)):
            html = client.post("/calculate", data={"operation": "add", "a": "2", "b": "3"}).data.decode()
        assert "addition" in html.lower()


# ===========================================================================
# POST /calculate  — multiplication
# ===========================================================================

class TestMultiplication:
    def test_multiply_integers_returns_200(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("multiply", 15.0, 3.0, 5.0)):
            response = client.post("/calculate", data={"operation": "multiply", "a": "3", "b": "5"})
        assert response.status_code == 200

    def test_multiply_integers_shows_result(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("multiply", 15.0, 3.0, 5.0)):
            html = client.post("/calculate", data={"operation": "multiply", "a": "3", "b": "5"}).data.decode()
        assert "15.0" in html

    def test_multiply_floats_returns_200(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("multiply", 6.25, 2.5, 2.5)):
            response = client.post("/calculate", data={"operation": "multiply", "a": "2.5", "b": "2.5"})
        assert response.status_code == 200

    def test_multiply_floats_shows_result(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("multiply", 6.25, 2.5, 2.5)):
            html = client.post("/calculate", data={"operation": "multiply", "a": "2.5", "b": "2.5"}).data.decode()
        assert "6.25" in html

    def test_multiply_shows_multiplication_label(self, client):
        with patch("fe.app.call_backend", return_value=fake_backend("multiply", 6.0, 2.0, 3.0)):
            html = client.post("/calculate", data={"operation": "multiply", "a": "2", "b": "3"}).data.decode()
        assert "multiplication" in html.lower()
