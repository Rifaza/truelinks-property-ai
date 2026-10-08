from app.agents.photo_issue_agent import PhotoIssueAgent
from app.schemas.photo_issue import PhotoIssueResult


def test_photo_issue_agent_returns_structured_result():
    result = PhotoIssueAgent().analyze(
        image_path="tests/fixtures/water_leakage.jpg",
        affected_unit="MC-B-1204",
    )

    assert isinstance(result, PhotoIssueResult)

    assert result.issue == "Water leakage"
    assert result.description
    assert result.severity == "HIGH"

    assert result.condition == "Damaged"

    assert "Ceiling fixture" in result.visible_items
    assert "Air conditioning unit" in result.visible_items

    assert result.work_order.title
    assert result.work_order.description
    assert result.work_order.affected_unit == "MC-B-1204"
    assert result.work_order.recommended_action