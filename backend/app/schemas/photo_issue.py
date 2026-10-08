from pydantic import BaseModel, Field


class VisionAnalysis(BaseModel):
    condition: str
    visible_items: list[str] = Field(default_factory=list)
    issue: str
    description: str
    severity: str


class WorkOrderDraft(BaseModel):
    title: str
    description: str
    affected_unit: str
    recommended_action: str


class PhotoIssueResult(BaseModel):
    issue: str
    description: str
    severity: str
    condition: str
    visible_items: list[str] = Field(default_factory=list)
    work_order: WorkOrderDraft