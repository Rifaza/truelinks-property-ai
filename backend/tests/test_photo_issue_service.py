from app.models.property_issue import PropertyIssue
from app.models.work_order import WorkOrder
from app.schemas.photo_issue import PhotoIssueResult, WorkOrderDraft
from app.services.photo_issue_service import PhotoIssueService


def test_photo_issue_service_persists_issue_and_work_order(db_session):
    result = PhotoIssueResult(
        issue="Water leakage",
        description="Visible water staining around the ceiling.",
        severity="HIGH",
        condition="Damaged",
        visible_items=[
            "Ceiling fixture",
            "Air conditioning unit",
        ],
        work_order=WorkOrderDraft(
            title="Inspect water leakage",
            description="Visible water staining around the ceiling.",
            affected_unit="MC-B-1204",
            recommended_action=(
                "Inspect the affected area and address the water leakage."
            ),
        ),
    )

    issue = PhotoIssueService().create_issue_and_work_order(
        db=db_session,
        unit_id=1,
        result=result,
    )

    assert issue.id is not None
    assert issue.issue == "Water leakage"
    assert issue.severity == "HIGH"
    assert issue.condition == "Damaged"
    assert issue.status == "OPEN"

    work_order = db_session.query(WorkOrder).filter(
        WorkOrder.issue_id == issue.id
    ).one()

    assert work_order.title == "Inspect water leakage"
    assert work_order.affected_unit == "MC-B-1204"
    assert work_order.status == "DRAFT"