from app.agents.lease_extraction_agent import LeaseExtractionAgent


def test_lease_extraction_returns_required_fields():
    result = LeaseExtractionAgent().extract("sample.pdf")

    assert result.landlord_name is not None
    assert result.tenant_name is not None
    assert result.unit_number == "MC-B-1204"
    assert result.monthly_rent == 10000
    assert result.annual_rent == 120000
    assert result.deposit_amount == 10000
    assert result.term_months == 12
    assert result.escalation_terms is not None


def test_lease_extraction_returns_evidence():
    result = LeaseExtractionAgent().extract("sample.pdf")

    assert len(result.evidence) > 0

    evidence_fields = {
        evidence.field_name
        for evidence in result.evidence
    }

    assert "monthly_rent" in evidence_fields
    assert "deposit_amount" in evidence_fields
    assert "unit_number" in evidence_fields