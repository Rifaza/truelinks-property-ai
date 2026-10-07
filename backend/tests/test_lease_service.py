from decimal import Decimal

from app.agents.lease_extraction_agent import LeaseExtractionAgent
from app.db.database import SessionLocal
from app.models import Evidence, Lease
from app.services.lease_service import LeaseService
from app.services.unit_matcher import UnitMatcher


def test_create_lease_from_extraction_persists_lease_and_evidence():
    extraction = LeaseExtractionAgent().extract("sample.pdf")

    db = SessionLocal()

    try:
        unit = UnitMatcher().find_unit(
            db,
            extraction.unit_number,
        )

        assert unit is not None

        unit_id = unit.id

    finally:
        db.close()

    lease = LeaseService().create_lease_from_extraction(
        extraction=extraction,
        source_filename="sample.pdf",
        unit_id=unit_id,
    )

    db = SessionLocal()

    try:
        saved_lease = db.query(Lease).filter(
            Lease.id == lease.id
        ).first()

        assert saved_lease is not None
        assert saved_lease.unit_id == unit_id
        assert saved_lease.monthly_rent == Decimal("10000")
        assert saved_lease.annual_rent == Decimal("120000")
        assert saved_lease.deposit_amount == Decimal("10000")
        assert saved_lease.term_months == 12

        evidence = db.query(Evidence).filter(
            Evidence.lease_id == saved_lease.id
        ).all()

        assert len(evidence) > 0

        evidence_fields = {
            item.field_name
            for item in evidence
        }

        assert "monthly_rent" in evidence_fields
        assert "deposit_amount" in evidence_fields
        assert "unit_number" in evidence_fields

    finally:
        db.close()