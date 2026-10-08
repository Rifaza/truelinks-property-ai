from app.agents.stub_vision_model import StubVisionModel
from app.agents.vision_model import VisionModel
from app.schemas.photo_issue import (
    PhotoIssueResult,
    WorkOrderDraft,
)


class PhotoIssueAgent:
    """
    Converts visual observations from a vision model into a
    structured property issue and draft work order.
    """

    def __init__(
        self,
        vision_model: VisionModel | None = None,
    ):
        self.vision_model = (
            vision_model
            if vision_model is not None
            else StubVisionModel()
        )

    def analyze(
        self,
        image_path: str,
        affected_unit: str = "Unknown",
    ) -> PhotoIssueResult:
        vision_result = self.vision_model.analyze(
            image_path
        )

        work_order = WorkOrderDraft(
            title=f"Inspect {vision_result.issue.lower()}",
            description=vision_result.description,
            affected_unit=affected_unit,
            recommended_action=(
                f"Inspect the affected area and address "
                f"the reported {vision_result.issue.lower()}."
            ),
        )

        return PhotoIssueResult(
            issue=vision_result.issue,
            description=vision_result.description,
            severity=vision_result.severity,
            condition=vision_result.condition,
            visible_items=vision_result.visible_items,
            work_order=work_order,
        )