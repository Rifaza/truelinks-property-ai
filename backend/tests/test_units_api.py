from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_unit_overview_returns_unit():
    response = client.get("/api/units/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["unit_number"] == "MC-B-1204"
    assert data["label"] == "Apartment 1204"
    assert data["unit_type"] == "2BR"
    assert data["status"] == "available"
    assert "lease" in data
    assert "issues" in data


def test_get_unknown_unit_returns_404():
    response = client.get("/api/units/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Unit with id 999999 not found."
    )