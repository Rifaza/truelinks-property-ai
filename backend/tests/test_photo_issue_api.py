from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_photo_returns_work_order():
    response = client.post(
        "/api/photos/analyze",
        data={
            "affected_unit": "MC-B-1204",
        },
        files={
            "file": (
                "water_leakage.jpg",
                BytesIO(b"fake image content"),
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["issue"] == "Water leakage"
    assert data["description"]
    assert data["severity"] == "HIGH"
    assert data["condition"] == "Damaged"

    assert "Ceiling fixture" in data["visible_items"]
    assert "Air conditioning unit" in data["visible_items"]

    assert data["work_order"]["title"] == (
        "Inspect water leakage"
    )

    assert data["work_order"]["affected_unit"] == (
        "MC-B-1204"
    )

    assert data["work_order"]["description"]
    assert data["work_order"]["recommended_action"]


def test_analyze_photo_rejects_unsupported_file_type():
    response = client.post(
        "/api/photos/analyze",
        data={
            "affected_unit": "MC-B-1204",
        },
        files={
            "file": (
                "document.pdf",
                BytesIO(b"fake pdf content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only JPEG, PNG, and WebP images are supported."
    )


def test_analyze_photo_rejects_empty_file():
    response = client.post(
        "/api/photos/analyze",
        data={
            "affected_unit": "MC-B-1204",
        },
        files={
            "file": (
                "empty.jpg",
                BytesIO(b""),
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Photo file is empty."
    )


def test_analyze_photo_requires_affected_unit():
    response = client.post(
        "/api/photos/analyze",
        files={
            "file": (
                "water_leakage.jpg",
                BytesIO(b"fake image content"),
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 422