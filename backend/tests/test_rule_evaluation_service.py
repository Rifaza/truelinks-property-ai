from app.db.database import SessionLocal
from app.models import Evidence, Lease, RuleResult, RuleResultEvidence
from app.services.rule_evaluation_service import RuleEvaluationService


def test_rule_evaluation_persists_results_and_evidence():
    db = SessionLocal()

    try:
        lease = db.query(Lease).first()
        assert lease is not None

        lease_id = lease.id

        existing_result_ids = {
            result.id
            for result in (
                db.query(RuleResult)
                .filter(RuleResult.lease_id == lease_id)
                .all()
            )
        }

    finally:
        db.close()

    db = SessionLocal()

    try:
        lease = db.get(Lease, lease_id)
        assert lease is not None

        RuleEvaluationService().evaluate_and_persist(lease)

    finally:
        db.close()

    db = SessionLocal()

    try:
        persisted_results = (
            db.query(RuleResult)
            .filter(RuleResult.lease_id == lease_id)
            .all()
        )

        new_results = [
            result
            for result in persisted_results
            if result.id not in existing_result_ids
        ]

        assert len(new_results) == 7

        statuses = {
            result.rule_id: result.status
            for result in new_results
        }

        assert statuses["R1"] == "PASS"
        assert statuses["R2"] == "PASS"
        assert statuses["R3"] == "PASS"
        assert statuses["R4"] == "PASS"
        assert statuses["R5"] == "PASS"
        assert statuses["R6"] == "PASS"
        assert statuses["R7"] == "PASS"

        new_results.sort(key=lambda result: result.rule_id)

        assert [result.rule_id for result in new_results] == [
            "R1",
            "R2",
            "R3",
            "R4",
            "R5",
            "R6",
            "R7",
        ]

        new_result_ids = {
            result.id
            for result in new_results
        }

        association_rows = (
            db.query(RuleResultEvidence)
            .filter(
                RuleResultEvidence.rule_result_id.in_(
                    new_result_ids
                )
            )
            .all()
        )

        assert len(association_rows) > 0

        evidence_ids = {
            row.evidence_id
            for row in association_rows
        }

        lease_evidence_ids = {
            evidence.id
            for evidence in (
                db.query(Evidence)
                .filter(Evidence.lease_id == lease_id)
                .all()
            )
        }

        assert evidence_ids.issubset(lease_evidence_ids)

        linked_evidence_fields = {
            evidence.field_name
            for evidence in (
                db.query(Evidence)
                .filter(Evidence.id.in_(evidence_ids))
                .all()
            )
        }

        assert "deposit_amount" in linked_evidence_fields
        assert "monthly_rent" in linked_evidence_fields
        assert "annual_rent" in linked_evidence_fields
        assert "start_date" in linked_evidence_fields
        assert "end_date" in linked_evidence_fields
        assert "term_months" in linked_evidence_fields
        assert "tenant_signed" in linked_evidence_fields
        assert "landlord_signed" in linked_evidence_fields
        assert "escalation_terms" in linked_evidence_fields

    finally:
        db.close()