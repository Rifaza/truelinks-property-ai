from abc import ABC, abstractmethod

from app.schemas.photo_issue import VisionAnalysis


class VisionModel(ABC):
    """
    Interface for a property-photo vision model.

    A production implementation can call a real vision API.
    The assessment uses a local stub implementation.
    """

    @abstractmethod
    def analyze(
        self,
        image_path: str,
    ) -> VisionAnalysis:
        raise NotImplementedError