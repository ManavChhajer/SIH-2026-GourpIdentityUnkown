import asyncio
import random
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fixtures import pick_fixture

app = FastAPI(title="Land Record Digitizer — Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# In-memory document store (no DB — mocked demo tier).
# Each record: document_id, filename, processed_at, fields, overall_confidence,
# review_required, status ("auto_approved" | "pending_review" | "approved" | "boundary_drawn"),
# boundary (list of [x, y] points, only set once hand-drawn).
DOCUMENTS: Dict[str, dict] = {}


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
    record = {
        "document_id": document_id,
        "filename": file.filename,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "fields": fixture["fields"],
        "overall_confidence": overall_confidence,
        "review_required": review_required,
        "status": "pending_review" if review_required else "auto_approved",
        "boundary": None,
    }
    DOCUMENTS[document_id] = record
    return record


@app.get("/api/documents")
def list_documents(status: Optional[str] = None):
    docs = list(DOCUMENTS.values())
    if status:
        docs = [d for d in docs if d["status"] == status]
    docs.sort(key=lambda d: d["processed_at"], reverse=True)
    return {"documents": docs}


@app.get("/api/documents/{document_id}")
def get_document(document_id: str):
    doc = DOCUMENTS.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


@app.post("/api/documents/{document_id}/approve")
def approve_document(document_id: str):
    doc = DOCUMENTS.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    doc["status"] = "approved"
    return doc


class BoundaryPayload(BaseModel):
    points: List[List[float]]


@app.post("/api/documents/{document_id}/boundary")
def save_boundary(document_id: str, payload: BoundaryPayload):
    doc = DOCUMENTS.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    if len(payload.points) < 3:
        raise HTTPException(status_code=422, detail="boundary needs at least 3 points")
    doc["boundary"] = payload.points
    doc["status"] = "boundary_drawn"
    return doc
