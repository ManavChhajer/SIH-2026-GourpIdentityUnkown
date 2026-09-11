import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _upload(filename="khata_page_03.jpg"):
    file_content = io.BytesIO(b"fake-image-bytes")
    return client.post(
        "/api/analyze",
        files={"file": (filename, file_content, "image/jpeg")},
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
