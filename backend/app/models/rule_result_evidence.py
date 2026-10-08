from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class RuleResultEvidence(Base):
    """
    Association table connecting rule results with their supporting evidence.

    A rule can use multiple evidence records, and the same evidence can
    support multiple rule results.
    """

    __tablename__ = "rule_result_evidence"

    # Identifies the rule result using this evidence.
    rule_result_id: Mapped[int] = mapped_column(
        ForeignKey("rule_results.id"),
        primary_key=True,
    )

    # Identifies the evidence supporting the rule result.
    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id"),
        primary_key=True,
    )