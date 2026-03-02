from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Calculator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class OperationRequest(BaseModel):
    a: float
    b: float


class OperationResult(BaseModel):
    a: float
    b: float
    result: float
    operation: str


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Calculator API"}


@app.post("/add", response_model=OperationResult)
def add(payload: OperationRequest):
    num1 = payload.a
    num2 = payload.b
    result = num1 + num2
    return OperationResult(
        a=num1,
        b=num2,
        result=result,
        operation="addition",
    )


@app.post("/multiply", response_model=OperationResult)
def multiply(payload: OperationRequest):
    return OperationResult(
        a=payload.a,
        b=payload.b,
        result=payload.a * payload.b,
        operation="multiplication",
    )
