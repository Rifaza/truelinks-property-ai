from datetime import date
from decimal import Decimal

from app.schemas.lease import EvidenceItem, LeaseExtractionResult


class LeaseExtractionAgent:
    """
    Extracts structured lease information from a lease document.

    This first implementation is deterministic so that the complete
    application flow can be developed and evaluated without depending
    on an external LLM or document AI provider.

    The agent interface can later be replaced with a real extraction
    model while keeping the same LeaseExtractionResult contract.
    """

    def extract(self, filename: str) -> LeaseExtractionResult:
        """
        Return structured lease information for a sample lease.

        The sample values are intentionally aligned with the Marina Crest
        owner rules and are used to establish the extraction pipeline.
        """

        return LeaseExtractionResult(
            landlord_name="Marina Crest Holdings W.L.L.",
            tenant_name="Sample Tenant",
            unit_number="MC-B-1204",
            monthly_rent=Decimal("10000"),
            annual_rent=Decimal("120000"),
            deposit_amount=Decimal("10000"),
            start_date=date(2026, 11, 1),
            end_date=date(2027, 10, 31),
            term_months=12,
            escalation_terms="5% annual increase",
            landlord_signed=True,
            tenant_signed=True,
            evidence=[
                EvidenceItem(
                    field_name="landlord_name",
                    source_reference="page 1",
                    source_text="Landlord: Marina Crest Holdings W.L.L.",
                    confidence=0.99,
                ),
                EvidenceItem(
                    field_name="tenant_name",
                    source_reference="page 1",
                    source_text="Tenant: Sample Tenant",
                    confidence=0.99,
                ),
                EvidenceItem(
                    field_name="unit_number",
                    source_reference="page 1",
                    source_text="Premises: MC-B-1204",
                    confidence=0.98,
                ),
                EvidenceItem(
                    field_name="monthly_rent",
                    source_reference="page 2",
                    source_text="Monthly rent shall be QAR 10,000.",
                    confidence=0.97,
                ),
                EvidenceItem(
                    field_name="annual_rent",
                    source_reference="page 2",
                    source_text="Annual rent shall be QAR 120,000.",
                    confidence=0.97,
                ),
                EvidenceItem(
                    field_name="deposit_amount",
                    source_reference="page 2",
                    source_text="Security deposit: QAR 10,000.",
                    confidence=0.97,
                ),
                EvidenceItem(
                    field_name="start_date",
                    source_reference="page 1",
                    source_text="Commencement date: 1 November 2026.",
                    confidence=0.96,
                ),
                EvidenceItem(
                    field_name="end_date",
                    source_reference="page 1",
                    source_text="Expiry date: 31 October 2027.",
                    confidence=0.96,
                ),
                EvidenceItem(
                    field_name="term_months",
                    source_reference="page 1",
                    source_text="Lease term: 12 months.",
                    confidence=0.96,
                ),
                EvidenceItem(
                    field_name="escalation_terms",
                    source_reference="page 3",
                    source_text="Rent shall increase by 5% annually.",
                    confidence=0.95,
                ),
                EvidenceItem(
                    field_name="landlord_signed",
                    source_reference="page 4",
                    source_text="Landlord signature present.",
                    confidence=0.94,
                ),
                EvidenceItem(
                    field_name="tenant_signed",
                    source_reference="page 4",
                    source_text="Tenant signature present.",
                    confidence=0.94,
                ),
            ],
        )