import asyncio
import random
import uuid
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import government_records
from dummy_plot_fixtures import get_dummy_fixture
from fixtures import pick_fixture

app = FastAPI(title="Land Record Digitizer — Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db.init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- auth (uploader accounts — separate from the mocked Gov Employee login) ----------

class AuthPayload(BaseModel):
    username: str
    password: str


@app.post("/api/auth/signup")
def signup(payload: AuthPayload):
    result = db.create_user(payload.username.strip(), payload.password)
    if not result:
        raise HTTPException(status_code=409, detail="username already taken")
    return result


@app.post("/api/auth/login")
def login(payload: AuthPayload):
    result = db.authenticate_user(payload.username.strip(), payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="invalid username or password")
    return result


def _resolve_owner(x_auth_token: Optional[str]) -> Optional[str]:
    if not x_auth_token:
        return None
    return db.get_user_by_token(x_auth_token)


# ---------- documents ----------

@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
):
    await asyncio.sleep(random.uniform(1.2, 2.5))

    fixture = pick_fixture(file.filename)
    confidences = [f["confidence"] for f in fixture["fields"]]
    overall_confidence = round(sum(confidences) / len(confidences), 2)
    review_required = fixture["review_required"]

    owner_username = _resolve_owner(x_auth_token)

    document_id = f"doc_{uuid.uuid4().hex[:8]}"
    record = db.create_document(
        document_id=document_id,
        filename=file.filename,
        fields=fixture["fields"],
        overall_confidence=overall_confidence,
        review_required=review_required,
        status="pending_review" if review_required else "auto_approved",
        owner_username=owner_username,
    )
    return record


@app.get("/api/documents")
def list_documents(
    status: Optional[str] = None,
    x_auth_token: Optional[str] = Header(None, alias="X-Auth-Token"),
    mine: bool = False,
):
    owner_username = _resolve_owner(x_auth_token) if mine else None
    return {"documents": db.list_documents(status=status, owner_username=owner_username)}


@app.get("/api/documents/{document_id}")
def get_document(document_id: str):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


# ---------- dummy plot upload + government records (for judge demo / AI-accuracy review) ----------

class DummyUploadPayload(BaseModel):
    plot_id: int


@app.post("/api/documents/dummy-upload")
def dummy_upload(payload: DummyUploadPayload):
    fixture = get_dummy_fixture(payload.plot_id)
    if not fixture:
        raise HTTPException(status_code=404, detail="unknown plot_id — expected 1-4")

    confidences = [f["confidence"] for f in fixture["fields"]]
    overall_confidence = round(sum(confidences) / len(confidences), 2)
    review_required = fixture["review_required"]

    document_id = f"doc_{uuid.uuid4().hex[:8]}"
    record = db.create_document(
        document_id=document_id,
        filename=f"dummy_plot_{payload.plot_id}.jpg",
        fields=fixture["fields"],
        overall_confidence=overall_confidence,
        review_required=review_required,
        status="pending_review" if review_required else "auto_approved",
        plot_id=str(payload.plot_id),
    )
    return record


@app.get("/api/government-records")
def list_govt_records():
    return {"records": government_records.list_government_records()}


@app.get("/api/government-records/{plot_id}")
def get_govt_record(plot_id: int):
    record = government_records.get_government_record(plot_id)
    if not record:
        raise HTTPException(status_code=404, detail="unknown plot_id — expected 1-4")
    return record


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
