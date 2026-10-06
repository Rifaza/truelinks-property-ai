from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Evidence(Base):
    """
    Stores the source evidence supporting values extracted from a lease.

    Evidence allows the system to trace an extracted field back to
    the original document and helps reviewers verify AI output.
    """

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Links this evidence record to the lease it supports.
    lease_id: Mapped[int] = mapped_column(
        ForeignKey("leases.id"),
        nullable=False,
    )

    # Name of the lease field supported by this evidence.
    # Example: "monthly_rent", "deposit_amount", or "start_date".
    field_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Identifies where the evidence came from.
    # Example: "lease_document", "manual_review", or "system".
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Reference to the exact source location.
    # Example: "page 2" or "page 3, section 4".
    source_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Stores the original text supporting the extracted field value.
    # This allows a human reviewer to verify the AI extraction.
    source_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Confidence score assigned to the extracted value.
    # Helps identify fields that may require human review.
    confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    # Links this evidence record back to the lease it supports.
    lease: Mapped["Lease"] = relationship(
        back_populates="evidence",
    )

    # Links this evidence to all rule results that use it.
    rule_results: Mapped[list["RuleResult"]] = relationship(
        secondary="rule_result_evidence",
        back_populates="evidence",
    )