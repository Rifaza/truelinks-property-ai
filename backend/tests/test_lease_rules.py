from app.agents.lease_extraction_agent import LeaseExtractionAgent
from app.db.database import SessionLocal
from app.rules.lease_rules import LeaseRulesEngine
from app.schemas.rules import RuleStatus
from app.services.unit_matcher import UnitMatcher
from datetime import date


def test_all_rules_pass_for_valid_lease():
    lease = LeaseExtractionAgent().extract("sample.pdf")

    db = SessionLocal()

    try:
        unit = UnitMatcher().find_unit(
            db,
            lease.unit_number,
        )

        assert unit is not None

        results = LeaseRulesEngine().evaluate(
            lease,
            unit,
        )

    finally:
        db.close()

    assert len(results) == 7

    statuses = {
        result.rule_id: result.status
        for result in results
    }

    assert statuses["R1"] == RuleStatus.PASS
    assert statuses["R2"] == RuleStatus.PASS
    assert statuses["R3"] == RuleStatus.PASS
    assert statuses["R4"] == RuleStatus.PASS
    assert statuses["R5"] == RuleStatus.PASS
    assert statuses["R6"] == RuleStatus.PASS
    assert statuses["R7"] == RuleStatus.PASS


def test_r1_fails_when_deposit_is_less_than_monthly_rent():
    lease = LeaseExtractionAgent().extract("sample.pdf")
    lease.deposit_amount = 5000

    results = LeaseRulesEngine().evaluate(lease, None)

    r1 = next(result for result in results if result.rule_id == "R1")

    assert r1.status == RuleStatus.FAIL


def test_r2_is_not_determinable_for_vague_escalation():
    lease = LeaseExtractionAgent().extract("sample.pdf")
    lease.escalation_terms = "as mutually agreed"

    results = LeaseRulesEngine().evaluate(lease, None)

    r2 = next(result for result in results if result.rule_id == "R2")

    assert r2.status == RuleStatus.NOT_DETERMINABLE


def test_r3_fails_when_term_exceeds_36_months():
    lease = LeaseExtractionAgent().extract("sample.pdf")
    lease.term_months = 48

    results = LeaseRulesEngine().evaluate(lease, None)

    r3 = next(result for result in results if result.rule_id == "R3")

    assert r3.status == RuleStatus.FAIL


def test_r4_fails_when_dates_do_not_match_term():
    lease = LeaseExtractionAgent().extract("sample.pdf")
    lease.term_months = 24

    results = LeaseRulesEngine().evaluate(lease, None)

    r4 = next(result for result in results if result.rule_id == "R4")

    assert r4.status == RuleStatus.FAIL


def test_r5_fails_when_tenant_is_not_signed():
    lease = LeaseExtractionAgent().extract("sample.pdf")
    lease.tenant_signed = False

    results = LeaseRulesEngine().evaluate(lease, None)

    r5 = next(result for result in results if result.rule_id == "R5")

    assert r5.status == RuleStatus.FAIL


def test_r6_fails_when_annual_rent_does_not_reconcile():
    lease = LeaseExtractionAgent().extract("sample.pdf")
    lease.annual_rent = 100000

    results = LeaseRulesEngine().evaluate(lease, None)

    r6 = next(result for result in results if result.rule_id == "R6")

    assert r6.status == RuleStatus.FAIL


def test_r7_fails_for_unknown_unit():
    lease = LeaseExtractionAgent().extract("sample.pdf")

    results = LeaseRulesEngine().evaluate(
        lease,
        None,
    )

    r7 = next(result for result in results if result.rule_id == "R7")

    assert r7.status == RuleStatus.FAIL

def test_r4_accepts_first_day_to_last_day_previous_month():
    lease = LeaseExtractionAgent().extract("sample.pdf")

    lease.start_date = date(2026, 11, 1)
    lease.end_date = date(2027, 10, 31)
    lease.term_months = 12

    results = LeaseRulesEngine().evaluate(
        lease,
        None,
    )

    r4 = next(
        result
        for result in results
        if result.rule_id == "R4"
    )

    assert r4.status == RuleStatus.PASS