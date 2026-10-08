from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Lease(Base):
    """
    Represents lease information extracted from a lease document.

    The extracted values are later validated against the owner's
    ruleset by the lease rules engine.
    """

    __tablename__ = "leases"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Links the lease to the matched property unit.
    unit_id: Mapped[int] = mapped_column(
        ForeignKey("units.id"),
        nullable=False,
    )

    landlord_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tenant_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Used by rent-related rules, including deposit and annual-rent checks.
    monthly_rent: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Used to verify annual rent consistency:
    # annual rent = monthly rent × 12.
    annual_rent: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Used by R1: deposit must be at least one month's rent.
    deposit_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Used by lease term and date consistency rules.
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Used by lease term and date consistency rules, including R3.
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Stated lease duration used by R3 and R4.
    term_months: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    # Used by R2 to determine whether an escalation clause is defined.
    escalation_terms: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # Used by R5 to verify that the landlord has signed the lease.
    landlord_signed: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    # Used by R5 to verify that the tenant has signed the lease.
    tenant_signed: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    # Keeps track of the original document from which the lease was extracted.
    source_filename: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Links this lease to its property unit.
    unit: Mapped["Unit"] = relationship(
        back_populates="leases",
    )

    # A lease can have multiple evidence records supporting extracted fields.
    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="lease",
    )

    # A lease can have multiple rule results from the rules engine.
    rule_results: Mapped[list["RuleResult"]] = relationship(
        back_populates="lease",
    )