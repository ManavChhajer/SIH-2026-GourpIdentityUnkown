import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _upload(filename="khata_page_03.jpg", token=None):
    file_content = io.BytesIO(b"fake-image-bytes")
    headers = {"X-Auth-Token": token} if token else {}
    return client.post(
        "/api/analyze",
        files={"file": (filename, file_content, "image/jpeg")},
        headers=headers,
    )


def test_analyze_returns_expected_shape():
    response = _upload()
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "khata_page_03.jpg"
    assert "document_id" in body
    assert "processed_at" in body
    assert len(body["fields"]) == 6
    assert isinstance(body["overall_confidence"], float)
    assert isinstance(body["review_required"], bool)
    assert body["status"] in ("pending_review", "auto_approved")
    assert body["owner_username"] is None


def test_analyze_missing_file_returns_422():
    response = client.post("/api/analyze")
    assert response.status_code == 422


def test_list_documents_includes_uploaded_doc():
    upload = _upload("khata_page_99.jpg")
    doc_id = upload.json()["document_id"]
    response = client.get("/api/documents")
    assert response.status_code == 200
    ids = [d["document_id"] for d in response.json()["documents"]]
    assert doc_id in ids


def test_approve_document_updates_status():
    upload = _upload("khata_page_88.jpg")
    doc_id = upload.json()["document_id"]
    response = client.post(f"/api/documents/{doc_id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_approve_missing_document_returns_404():
    response = client.post("/api/documents/doc_missing/approve")
    assert response.status_code == 404


def test_save_boundary_requires_three_points():
    upload = _upload("khata_page_77.jpg")
    doc_id = upload.json()["document_id"]
    response = client.post(f"/api/documents/{doc_id}/boundary", json={"points": [[1, 1], [2, 2]]})
    assert response.status_code == 422


def test_save_boundary_success_updates_status_and_points():
    upload = _upload("khata_page_66.jpg")
    doc_id = upload.json()["document_id"]
    points = [[1, 1], [2, 2], [3, 1]]
    response = client.post(f"/api/documents/{doc_id}/boundary", json={"points": points})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "boundary_drawn"
    assert body["boundary"] == points


def test_signup_then_login_roundtrip():
    signup = client.post("/api/auth/signup", json={"username": "farmer1", "password": "hunter2"})
    assert signup.status_code == 200
    assert "token" in signup.json()

    login = client.post("/api/auth/login", json={"username": "farmer1", "password": "hunter2"})
    assert login.status_code == 200
    assert login.json()["username"] == "farmer1"


def test_signup_rejects_duplicate_username():
    client.post("/api/auth/signup", json={"username": "farmer2", "password": "pw"})
    dup = client.post("/api/auth/signup", json={"username": "farmer2", "password": "other"})
    assert dup.status_code == 409


def test_login_rejects_wrong_password():
    client.post("/api/auth/signup", json={"username": "farmer3", "password": "correct"})
    bad_login = client.post("/api/auth/login", json={"username": "farmer3", "password": "wrong"})
    assert bad_login.status_code == 401


def test_upload_with_token_sets_owner_and_mine_filters_correctly():
    signup = client.post("/api/auth/signup", json={"username": "farmer4", "password": "pw"})
    token = signup.json()["token"]

    upload = _upload("khata_page_55.jpg", token=token)
    assert upload.status_code == 200
    assert upload.json()["owner_username"] == "farmer4"

    mine = client.get("/api/documents", params={"mine": "true"}, headers={"X-Auth-Token": token})
    ids = [d["document_id"] for d in mine.json()["documents"]]
    assert upload.json()["document_id"] in ids

    # a doc uploaded without a token should not show up under "mine" for this user
    other_upload = _upload("khata_page_44.jpg")
    other_id = other_upload.json()["document_id"]
    mine_again = client.get("/api/documents", params={"mine": "true"}, headers={"X-Auth-Token": token})
    ids_again = [d["document_id"] for d in mine_again.json()["documents"]]
    assert other_id not in ids_again
