from app.db.database import SessionLocal
from app.models import Evidence, Lease
from app.schemas.lease import LeaseExtractionResult


class LeaseService:
    """
    Persists an extracted lease and its supporting evidence.

    The extraction agent produces structured facts.
    This service stores those facts and their provenance in PostgreSQL.
    """

    def create_lease_from_extraction(
        self,
        extraction: LeaseExtractionResult,
        source_filename: str,
        unit_id: int,
    ) -> Lease:
        db = SessionLocal()

        try:
            lease = Lease(
                unit_id=unit_id,
                landlord_name=extraction.landlord_name,
                tenant_name=extraction.tenant_name,
                monthly_rent=extraction.monthly_rent,
                annual_rent=extraction.annual_rent,
                deposit_amount=extraction.deposit_amount,
                start_date=extraction.start_date,
                end_date=extraction.end_date,
                term_months=extraction.term_months,
                escalation_terms=extraction.escalation_terms,
                landlord_signed=extraction.landlord_signed,
                tenant_signed=extraction.tenant_signed,
                source_filename=source_filename,
            )

            db.add(lease)
            db.flush()

            for item in extraction.evidence:
                evidence = Evidence(
                    lease_id=lease.id,
                    field_name=item.field_name,
                    source_type="lease_document",
                    source_reference=item.source_reference,
                    source_text=item.source_text,
                    confidence=item.confidence,
                )

                db.add(evidence)

            db.commit()
            db.refresh(lease)

            return lease

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()