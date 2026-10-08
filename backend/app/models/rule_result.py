from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class RuleResult(Base):
    """
    Stores the result of applying an owner rule to a lease.

    Each result records the rule decision, explanation, and supporting
    evidence so that the decision can be reviewed by a human.
    """

    __tablename__ = "rule_results"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Links the rule result to the lease being evaluated.
    lease_id: Mapped[int] = mapped_column(
        ForeignKey("leases.id"),
        nullable=False,
    )

    # Identifier of the owner rule being evaluated.
    # Example: "R1", "R2", "R3", etc.
    rule_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Final decision produced by the rules engine.
    # Expected values: PASS, FAIL, or NOT_DETERMINABLE.
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # Human-readable explanation of why the rule received this result.
    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Evidence supporting this rule decision.
    # A rule can reference multiple evidence records.
    evidence: Mapped[list["Evidence"]] = relationship(
        secondary="rule_result_evidence",
        back_populates="rule_results",
    )

    # Links this rule result back to the lease being evaluated.
    lease: Mapped["Lease"] = relationship(
        back_populates="rule_results",
    )