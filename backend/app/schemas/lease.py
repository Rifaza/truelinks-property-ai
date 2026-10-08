from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """
    Evidence supporting one extracted lease field.

    Keeping evidence with the extraction result allows the system
    to trace an AI-extracted value back to the original lease.
    """

    field_name: str = Field(
        description="Lease field supported by this evidence."
    )

    source_reference: str = Field(
        description="Location in the source document, such as page 2."
    )

    source_text: str = Field(
        description="Original text supporting the extracted value."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Extraction confidence between 0 and 1."
    )


class LeaseExtractionResult(BaseModel):
    """
    Structured output produced by the lease extraction agent.

    The fields are intentionally aligned with the owner's seven
    validation rules.
    """

    landlord_name: str | None = None

    tenant_name: str | None = None

    unit_number: str | None = None

    monthly_rent: Decimal | None = None

    annual_rent: Decimal | None = None

    deposit_amount: Decimal | None = None

    start_date: date | None = None

    end_date: date | None = None

    term_months: int | None = None

    escalation_terms: str | None = None

    landlord_signed: bool | None = None

    tenant_signed: bool | None = None

    evidence: list[EvidenceItem] = Field(
        default_factory=list,
    )