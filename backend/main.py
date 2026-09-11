import asyncio
import random
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from fixtures import pick_fixture

app = FastAPI(title="Land Record Digitizer — Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    await asyncio.sleep(random.uniform(1.2, 2.5))

    fixture = pick_fixture(file.filename)
    confidences = [f["confidence"] for f in fixture["fields"]]
    overall_confidence = round(sum(confidences) / len(confidences), 2)

    return {
        "document_id": f"doc_{uuid.uuid4().hex[:8]}",
        "filename": file.filename,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "fields": fixture["fields"],
        "overall_confidence": overall_confidence,
        "review_required": fixture["review_required"],
    }
