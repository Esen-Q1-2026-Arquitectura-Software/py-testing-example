import os
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")


def call_backend(endpoint: str, a: float, b: float) -> dict:
    """Call the FastAPI backend and return the JSON response."""
    url = f"{FASTAPI_BASE_URL}/{endpoint}"
    response = requests.post(url, json={"a": a, "b": b}, timeout=10)
    response.raise_for_status()
    return response.json()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    operation = request.form.get("operation")
    try:
        a = float(request.form.get("a", ""))
        b = float(request.form.get("b", ""))
    except ValueError:
        return render_template(
            "index.html",
            error="Please enter valid numbers.",
            a=request.form.get("a", ""),
            b=request.form.get("b", ""),
        )

    if operation not in ("add", "multiply"):
        return render_template("index.html", error="Unknown operation.", a=a, b=b)

    try:
        data = call_backend(operation, a, b)
    except requests.exceptions.ConnectionError:
        return render_template(
            "index.html",
            error="Could not connect to the backend. Make sure the FastAPI server is running on port 8000.",
            a=a,
            b=b,
        )
    except requests.exceptions.HTTPError as exc:
        return render_template(
            "index.html",
            error=f"Backend error: {exc}",
            a=a,
            b=b,
        )

    return render_template("result.html", data=data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
