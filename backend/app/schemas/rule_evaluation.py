from pydantic import BaseModel, Field

from app.schemas.rules import RuleStatus


class RuleEvidenceResponse(BaseModel):
    field_name: str
    source_reference: str | None = None
    source_text: str | None = None
    confidence: float | None = None


class RuleResultResponse(BaseModel):
    rule_id: str
    status: RuleStatus
    explanation: str
    evidence: list[RuleEvidenceResponse] = Field(
        default_factory=list
    )


class LeaseEvaluationResponse(BaseModel):
    lease_id: int
    rules: list[RuleResultResponse]