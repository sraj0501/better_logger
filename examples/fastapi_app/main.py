from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from narrative import OllamaFailureAnalyzer, stage, story

from .db import create_customer, init_db, list_customers

USE_OLLAMA = os.getenv("NARRATIVE_USE_OLLAMA", "0") == "1"
MODEL = os.getenv("NARRATIVE_OLLAMA_MODEL", "qwen2.5-coder:7b")
failure_analyzer = OllamaFailureAnalyzer(model=MODEL) if USE_OLLAMA else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    with story("FastAPI App Startup", failure_analyzer=failure_analyzer):
        with stage("Initialize Database"):
            init_db()
    try:
        yield
    finally:
        with story("FastAPI App Shutdown", failure_analyzer=failure_analyzer):
            with stage("Release Resources"):
                pass


app = FastAPI(title="Narrative Logging FastAPI Demo", version="0.1.0", lifespan=lifespan)


class CustomerCreate(BaseModel):
    name: str
    email: str


@app.get("/health")
def health() -> dict[str, str]:
    with story("Health Check", failure_analyzer=failure_analyzer):
        with stage("Build Response"):
            return {"status": "ok"}


@app.post("/customers")
def add_customer(payload: CustomerCreate) -> dict[str, object]:
    with story("Create Customer", failure_analyzer=failure_analyzer):
        with stage("Validate Input"):
            if "@" not in payload.email:
                raise ValueError("invalid email")

        with stage("Insert Into Database"):
            try:
                customer = create_customer(payload.name, payload.email)
            except ValueError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc

        with stage("Build Response"):
            return {"created": True, "customer": customer}


@app.get("/customers")
def get_customers() -> dict[str, object]:
    with story("List Customers", failure_analyzer=failure_analyzer):
        with stage("Fetch Customers"):
            customers = list_customers()

        with stage("Build Response"):
            return {"count": len(customers), "customers": customers}
