from __future__ import annotations

from app.db.database import SessionLocal
from app.models import Evidence, Lease, RuleResult, Unit
from app.rules.lease_rules import LeaseRulesEngine
from app.schemas.lease import EvidenceItem, LeaseExtractionResult


class RuleEvaluationService:
    """
    Orchestrates lease rule evaluation and persistence.

    LeaseRulesEngine:
        Pure business-rule evaluation.

    RuleEvaluationService:
        Database orchestration and persistence of rule results/evidence.
    """

    def evaluate_and_persist(self, lease: Lease) -> list[RuleResult]:
        """
        Evaluate a persisted lease against R1-R7 and persist the results.

        The operation is atomic:
        - all rule results and evidence links are committed together
        - any persistence failure rolls back the transaction
        """

        db = SessionLocal()

        try:
            # Re-load the lease inside this session so that all ORM
            # relationships are attached to the current transaction.
            persisted_lease = db.get(Lease, lease.id)

            if persisted_lease is None:
                raise ValueError(
                    f"Lease with id {lease.id} does not exist."
                )

            # Load the matched property unit used by R7.
            unit = db.get(Unit, persisted_lease.unit_id)

            # Convert the persisted ORM entity back into the schema
            # consumed by the pure rules engine.
            extraction = self._to_extraction_result(
                persisted_lease
            )

            # Business-rule evaluation remains completely separate
            # from database persistence.
            evaluations = LeaseRulesEngine().evaluate(
                extraction,
                unit,
            )

            persisted_results: list[RuleResult] = []

            for evaluation in evaluations:
                rule_result = RuleResult(
                    lease_id=persisted_lease.id,
                    rule_id=evaluation.rule_id,
                    status=evaluation.status.value,
                    explanation=evaluation.explanation,
                )

                db.add(rule_result)
                db.flush()

                # The rules engine returns EvidenceItem objects.
                # Match them against the persisted Evidence rows
                # belonging to this lease.
                evidence_by_field = {
                    evidence.field_name: evidence
                    for evidence in persisted_lease.evidence
                }

                linked_evidence: list[Evidence] = []

                for evidence_item in evaluation.evidence:
                    evidence = evidence_by_field.get(
                        evidence_item.field_name
                    )

                    if evidence is not None:
                        linked_evidence.append(evidence)

                rule_result.evidence.extend(linked_evidence)

                persisted_results.append(rule_result)

            # Commit all RuleResult rows and all association rows
            # as one atomic transaction.
            db.commit()

            # Refresh results so generated database IDs are available.
            # Also load evidence while the session is still open because
            # the API response needs rule-level provenance after this service
            # closes its database session.
            for result in persisted_results:
                db.refresh(result)
                result.evidence

            return persisted_results

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    @staticmethod
    def _to_extraction_result(
        lease: Lease,
    ) -> LeaseExtractionResult:
        """
        Convert a persisted Lease ORM entity into the schema expected
        by LeaseRulesEngine.
        """

        evidence = [
            EvidenceItem(
                field_name=item.field_name,
                source_reference=item.source_reference or "",
                source_text=item.source_text or "",
                confidence=item.confidence or 0.0,
            )
            for item in lease.evidence
        ]

        return LeaseExtractionResult(
            landlord_name=lease.landlord_name,
            tenant_name=lease.tenant_name,
            unit_number=lease.unit.unit_number if lease.unit else None,
            monthly_rent=lease.monthly_rent,
            annual_rent=lease.annual_rent,
            deposit_amount=lease.deposit_amount,
            start_date=lease.start_date,
            end_date=lease.end_date,
            term_months=lease.term_months,
            escalation_terms=lease.escalation_terms,
            landlord_signed=lease.landlord_signed,
            tenant_signed=lease.tenant_signed,
            evidence=evidence,
        )