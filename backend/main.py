import asyncio
import random
import uuid
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
from fixtures import pick_fixture

app = FastAPI(title="Land Record Digitizer — Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db.init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    await asyncio.sleep(random.uniform(1.2, 2.5))

    fixture = pick_fixture(file.filename)
    confidences = [f["confidence"] for f in fixture["fields"]]
    overall_confidence = round(sum(confidences) / len(confidences), 2)
    review_required = fixture["review_required"]

    document_id = f"doc_{uuid.uuid4().hex[:8]}"
    record = db.create_document(
        document_id=document_id,
        filename=file.filename,
        fields=fixture["fields"],
        overall_confidence=overall_confidence,
        review_required=review_required,
        status="pending_review" if review_required else "auto_approved",
    )
    return record


@app.get("/api/documents")
def list_documents(status: Optional[str] = None):
    return {"documents": db.list_documents(status=status)}


@app.get("/api/documents/{document_id}")
def get_document(document_id: str):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


@app.post("/api/documents/{document_id}/approve")
def approve_document(document_id: str):
    doc = db.update_status(document_id, "approved")
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


class BoundaryPayload(BaseModel):
    points: List[List[float]]


@app.post("/api/documents/{document_id}/boundary")
def save_boundary(document_id: str, payload: BoundaryPayload):
    if len(payload.points) < 3:
        raise HTTPException(status_code=422, detail="boundary needs at least 3 points")
    doc = db.save_boundary(document_id, payload.points)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return doc
