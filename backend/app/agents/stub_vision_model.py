from app.agents.vision_model import VisionModel
from app.schemas.photo_issue import VisionAnalysis


class StubVisionModel(VisionModel):
    """
    Deterministic vision-model substitute for local development
    and assessment testing.

    The stub represents the structured output that a real vision
    model would return after inspecting a property photo.
    """

    def analyze(
        self,
        image_path: str,
    ) -> VisionAnalysis:
        return VisionAnalysis(
            condition="Damaged",
            visible_items=[
                "Ceiling fixture",
                "Air conditioning unit",
            ],
            issue="Water leakage",
            description=(
                "Visible water staining and signs of leakage "
                "around the ceiling area."
            ),
            severity="HIGH",
        )