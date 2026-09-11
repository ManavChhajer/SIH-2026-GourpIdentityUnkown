import pytest

import db as db_module


def test_create_and_get_document():
    fields = [{"name": "khata_no", "label": "Khata No.", "value": "1", "confidence": 0.9}]
    created = db_module.create_document(
        document_id="doc_test1",
        filename="a.jpg",
        fields=fields,
        overall_confidence=0.9,
        review_required=False,
        status="auto_approved",
    )
    assert created["document_id"] == "doc_test1"

    fetched = db_module.get_document("doc_test1")
    assert fetched is not None
    assert fetched["filename"] == "a.jpg"
    assert fetched["fields"] == fields
    assert fetched["boundary"] is None


def test_list_documents_filters_by_status():
    db_module.create_document("doc_a", "a.jpg", [], 0.9, False, "auto_approved")
    db_module.create_document("doc_b", "b.jpg", [], 0.5, True, "pending_review")

    pending = db_module.list_documents(status="pending_review")
    assert [d["document_id"] for d in pending] == ["doc_b"]

    all_docs = db_module.list_documents()
    assert len(all_docs) == 2


def test_update_status_persists():
    db_module.create_document("doc_c", "c.jpg", [], 0.5, True, "pending_review")
    updated = db_module.update_status("doc_c", "approved")
    assert updated["status"] == "approved"

    refetched = db_module.get_document("doc_c")
    assert refetched["status"] == "approved"


def test_save_boundary_persists_points_and_status():
    db_module.create_document("doc_d", "d.jpg", [], 0.5, True, "pending_review")
    points = [[1, 1], [2, 2], [3, 1]]
    updated = db_module.save_boundary("doc_d", points)
    assert updated["status"] == "boundary_drawn"
    assert updated["boundary"] == points

    refetched = db_module.get_document("doc_d")
    assert refetched["boundary"] == points


def test_update_status_missing_document_returns_none():
    assert db_module.update_status("doc_missing", "approved") is None
