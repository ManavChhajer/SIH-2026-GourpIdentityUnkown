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


def test_create_document_with_owner_username():
    db_module.create_user("alice", "pw123")
    doc = db_module.create_document("doc_e", "e.jpg", [], 0.5, True, "pending_review", owner_username="alice")
    assert doc["owner_username"] == "alice"


def test_list_documents_filters_by_owner():
    db_module.create_user("bob", "pw123")
    db_module.create_document("doc_f", "f.jpg", [], 0.5, True, "pending_review", owner_username="bob")
    db_module.create_document("doc_g", "g.jpg", [], 0.5, True, "pending_review", owner_username=None)

    mine = db_module.list_documents(owner_username="bob")
    assert [d["document_id"] for d in mine] == ["doc_f"]


def test_create_user_rejects_duplicate_username():
    first = db_module.create_user("carol", "pw123")
    assert first is not None
    second = db_module.create_user("carol", "other")
    assert second is None


def test_authenticate_user_success_and_failure():
    db_module.create_user("dave", "correct-pw")
    ok = db_module.authenticate_user("dave", "correct-pw")
    assert ok is not None
    assert ok["username"] == "dave"

    bad = db_module.authenticate_user("dave", "wrong-pw")
    assert bad is None

    missing = db_module.authenticate_user("nobody", "whatever")
    assert missing is None


def test_get_user_by_token_roundtrip():
    result = db_module.create_user("erin", "pw123")
    username = db_module.get_user_by_token(result["token"])
    assert username == "erin"
    assert db_module.get_user_by_token("bogus-token") is None
