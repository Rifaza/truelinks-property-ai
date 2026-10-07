from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.lease import EvidenceItem


class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_DETERMINABLE = "NOT_DETERMINABLE"


class RuleEvaluation(BaseModel):
    rule_id: str = Field(
        description="Owner rule identifier, for example R1."
    )

    status: RuleStatus

    explanation: str

    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Evidence supporting the rule decision.",
    )