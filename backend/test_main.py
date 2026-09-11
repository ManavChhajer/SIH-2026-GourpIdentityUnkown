import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_analyze_returns_expected_shape():
    file_content = io.BytesIO(b"fake-image-bytes")
    response = client.post(
        "/api/analyze",
        files={"file": ("khata_page_03.jpg", file_content, "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "khata_page_03.jpg"
    assert "document_id" in body
    assert "processed_at" in body
    assert len(body["fields"]) == 6
    assert isinstance(body["overall_confidence"], float)
    assert isinstance(body["review_required"], bool)


def test_analyze_missing_file_returns_422():
    response = client.post("/api/analyze")
    assert response.status_code == 422
