from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.property_issue import PropertyIssue
from app.models.work_order import WorkOrder


client = TestClient(app)


def test_accept_work_order():
    db = SessionLocal()

    try:
        issue = PropertyIssue(
            unit_id=1,
            issue="Test leakage",
            description="Test issue",
            severity="HIGH",
            condition="Damaged",
            visible_items="Ceiling",
            status="OPEN",
        )

        db.add(issue)
        db.flush()

        work_order = WorkOrder(
            issue_id=issue.id,
            title="Test work order",
            description="Test description",
            affected_unit="MC-B-1204",
            recommended_action="Inspect issue",
            status="DRAFT",
        )

        db.add(work_order)
        db.commit()
        db.refresh(work_order)

        work_order_id = work_order.id

    finally:
        db.close()

    response = client.patch(
        f"/api/work-orders/{work_order_id}/accept"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ACCEPTED"


def test_reject_unknown_work_order():
    response = client.patch(
        "/api/work-orders/999999/reject"
    )

    assert response.status_code == 404