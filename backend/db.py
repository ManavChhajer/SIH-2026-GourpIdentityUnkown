"""SQLite persistence layer for the land-record digitizer (mocked-demo tier).

One table, `documents`, storing everything /api/analyze produces plus the
review-workflow state (status, boundary). fields/boundary are stored as
JSON text columns — this is a demo, not a normalized schema; a real build
would split fields into their own table.
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import create_engine, Column, String, Float, Boolean, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DB_PATH = os.path.join(os.path.dirname(__file__), "land_records.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    processed_at = Column(DateTime, nullable=False)
    fields_json = Column(Text, nullable=False)  # JSON-encoded list[dict]
    overall_confidence = Column(Float, nullable=False)
    review_required = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    boundary_json = Column(Text, nullable=True)  # JSON-encoded list[[x,y]] or null


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()


def _row_to_dict(row: Document) -> dict:
    return {
        "document_id": row.document_id,
        "filename": row.filename,
        "processed_at": row.processed_at.replace(tzinfo=timezone.utc).isoformat(),
        "fields": json.loads(row.fields_json),
        "overall_confidence": row.overall_confidence,
        "review_required": row.review_required,
        "status": row.status,
        "boundary": json.loads(row.boundary_json) if row.boundary_json else None,
    }


def create_document(
    document_id: str,
    filename: str,
    fields: list,
    overall_confidence: float,
    review_required: bool,
    status: str,
) -> dict:
    db = get_session()
    try:
        row = Document(
            document_id=document_id,
            filename=filename,
            processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            fields_json=json.dumps(fields),
            overall_confidence=overall_confidence,
            review_required=review_required,
            status=status,
            boundary_json=None,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _row_to_dict(row)
    finally:
        db.close()


def list_documents(status: Optional[str] = None) -> List[dict]:
    db = get_session()
    try:
        query = db.query(Document)
        if status:
            query = query.filter(Document.status == status)
        rows = query.order_by(Document.processed_at.desc()).all()
        return [_row_to_dict(r) for r in rows]
    finally:
        db.close()


def get_document(document_id: str) -> Optional[dict]:
    db = get_session()
    try:
        row = db.query(Document).filter(Document.document_id == document_id).first()
        return _row_to_dict(row) if row else None
    finally:
        db.close()


def update_status(document_id: str, status: str) -> Optional[dict]:
    db = get_session()
    try:
        row = db.query(Document).filter(Document.document_id == document_id).first()
        if not row:
            return None
        row.status = status
        db.commit()
        db.refresh(row)
        return _row_to_dict(row)
    finally:
        db.close()


def save_boundary(document_id: str, points: list) -> Optional[dict]:
    db = get_session()
    try:
        row = db.query(Document).filter(Document.document_id == document_id).first()
        if not row:
            return None
        row.boundary_json = json.dumps(points)
        row.status = "boundary_drawn"
        db.commit()
        db.refresh(row)
        return _row_to_dict(row)
    finally:
        db.close()
