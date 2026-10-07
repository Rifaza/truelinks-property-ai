

from app.models import Unit
from app.schemas.lease import EvidenceItem, LeaseExtractionResult
from app.schemas.rules import RuleEvaluation, RuleStatus

from calendar import monthrange
from datetime import date
from decimal import Decimal

class LeaseRulesEngine:
    """
    Deterministic implementation of the Marina Crest R1-R7 rules.

    The engine evaluates extracted facts only.
    It does not perform document extraction or modify the lease.
    """

    def evaluate(
        self,
        lease: LeaseExtractionResult,
        unit: Unit | None,
    ) -> list[RuleEvaluation]:
        return [
            self._evaluate_r1(lease),
            self._evaluate_r2(lease),
            self._evaluate_r3(lease),
            self._evaluate_r4(lease),
            self._evaluate_r5(lease),
            self._evaluate_r6(lease),
            self._evaluate_r7(unit),
        ]

    def _evaluate_r1(
        self,
        lease: LeaseExtractionResult,
    ) -> RuleEvaluation:
        evidence = self._evidence_for_fields(
            lease,
            {"deposit_amount", "monthly_rent"},
        )

        if (
            lease.deposit_amount is None
            or lease.monthly_rent is None
        ):
            return RuleEvaluation(
                rule_id="R1",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation=(
                    "Security deposit or monthly rent is missing, "
                    "so the minimum deposit requirement cannot be determined."
                ),
                evidence=evidence,
            )

        if lease.deposit_amount >= lease.monthly_rent:
            return RuleEvaluation(
                rule_id="R1",
                status=RuleStatus.PASS,
                explanation=(
                    f"Security deposit ({lease.deposit_amount}) is at least "
                    f"one month's rent ({lease.monthly_rent})."
                ),
                evidence=evidence,
            )

        return RuleEvaluation(
            rule_id="R1",
            status=RuleStatus.FAIL,
            explanation=(
                f"Security deposit ({lease.deposit_amount}) is less than "
                f"one month's rent ({lease.monthly_rent})."
            ),
            evidence=evidence,
        )

    def _evaluate_r2(
        self,
        lease: LeaseExtractionResult,
    ) -> RuleEvaluation:
        evidence = self._evidence_for_fields(
            lease,
            {"escalation_terms"},
        )

        if not lease.escalation_terms:
            return RuleEvaluation(
                rule_id="R2",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation="No rent escalation clause was extracted.",
                evidence=evidence,
            )

        normalized = lease.escalation_terms.lower().strip()

        vague_phrases = {
            "as mutually agreed",
            "to be mutually agreed",
            "as agreed",
            "to be agreed",
        }

        if normalized in vague_phrases:
            return RuleEvaluation(
                rule_id="R2",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation=(
                    "The escalation clause is vague and does not define "
                    "an actual mechanism or percentage."
                ),
                evidence=evidence,
            )

        return RuleEvaluation(
            rule_id="R2",
            status=RuleStatus.PASS,
            explanation=(
                f"A defined rent escalation mechanism was extracted: "
                f"{lease.escalation_terms}."
            ),
            evidence=evidence,
        )

    def _evaluate_r3(
        self,
        lease: LeaseExtractionResult,
    ) -> RuleEvaluation:
        evidence = self._evidence_for_fields(
            lease,
            {"term_months"},
        )

        if lease.term_months is None:
            return RuleEvaluation(
                rule_id="R3",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation="Lease term is missing.",
                evidence=evidence,
            )

        if lease.term_months <= 36:
            return RuleEvaluation(
                rule_id="R3",
                status=RuleStatus.PASS,
                explanation=(
                    f"Lease term is {lease.term_months} months, "
                    "which does not exceed 36 months."
                ),
                evidence=evidence,
            )

        return RuleEvaluation(
            rule_id="R3",
            status=RuleStatus.FAIL,
            explanation=(
                f"Lease term is {lease.term_months} months, "
                "which exceeds the 36-month limit."
            ),
            evidence=evidence,
        )

    def _evaluate_r4(
        self,
        lease: LeaseExtractionResult,
    ) -> RuleEvaluation:
        evidence = self._evidence_for_fields(
            lease,
            {"start_date", "end_date", "term_months"},
        )

        if (
            lease.start_date is None
            or lease.end_date is None
            or lease.term_months is None
        ):
            return RuleEvaluation(
                rule_id="R4",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation=(
                    "Commencement date, expiry date, or term length "
                    "is missing."
                ),
                evidence=evidence,
            )

        if lease.end_date <= lease.start_date:
            return RuleEvaluation(
                rule_id="R4",
                status=RuleStatus.FAIL,
                explanation=(
                    "Expiry date must be after the commencement date."
                ),
                evidence=evidence,
            )

        calculated_months = self._months_between(
            lease.start_date,
            lease.end_date,
        )

        if calculated_months != lease.term_months:
            return RuleEvaluation(
                rule_id="R4",
                status=RuleStatus.FAIL,
                explanation=(
                    f"The stated term is {lease.term_months} months, "
                    f"but the dates correspond to {calculated_months} months."
                ),
                evidence=evidence,
            )

        return RuleEvaluation(
            rule_id="R4",
            status=RuleStatus.PASS,
            explanation=(
                "Expiry date is after commencement date and the "
                "stated term matches the dates."
            ),
            evidence=evidence,
        )

    def _evaluate_r5(
        self,
        lease: LeaseExtractionResult,
    ) -> RuleEvaluation:
        evidence = self._evidence_for_fields(
            lease,
            {
                "landlord_name",
                "tenant_name",
                "landlord_signed",
                "tenant_signed",
            },
        )

        if (
            lease.landlord_name is None
            or lease.tenant_name is None
            or lease.landlord_signed is None
            or lease.tenant_signed is None
        ):
            return RuleEvaluation(
                rule_id="R5",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation=(
                    "Party identification or signature information "
                    "is incomplete."
                ),
                evidence=evidence,
            )

        if not lease.landlord_signed or not lease.tenant_signed:
            return RuleEvaluation(
                rule_id="R5",
                status=RuleStatus.FAIL,
                explanation=(
                    "Both landlord and tenant must sign the lease."
                ),
                evidence=evidence,
            )

        return RuleEvaluation(
            rule_id="R5",
            status=RuleStatus.PASS,
            explanation=(
                "Both landlord and tenant are identified and both "
                "signatures are present."
            ),
            evidence=evidence,
        )

    def _evaluate_r6(
        self,
        lease: LeaseExtractionResult,
    ) -> RuleEvaluation:
        evidence = self._evidence_for_fields(
            lease,
            {"monthly_rent", "annual_rent"},
        )

        if (
            lease.monthly_rent is None
            or lease.annual_rent is None
        ):
            return RuleEvaluation(
                rule_id="R6",
                status=RuleStatus.NOT_DETERMINABLE,
                explanation=(
                    "Monthly rent or annual rent is missing."
                ),
                evidence=evidence,
            )

        expected_annual = lease.monthly_rent * Decimal("12")

        if lease.annual_rent == expected_annual:
            return RuleEvaluation(
                rule_id="R6",
                status=RuleStatus.PASS,
                explanation=(
                    f"Annual rent ({lease.annual_rent}) equals "
                    f"monthly rent ({lease.monthly_rent}) × 12."
                ),
                evidence=evidence,
            )

        return RuleEvaluation(
            rule_id="R6",
            status=RuleStatus.FAIL,
            explanation=(
                f"Annual rent ({lease.annual_rent}) does not equal "
                f"monthly rent ({lease.monthly_rent}) × 12."
            ),
            evidence=evidence,
        )

    def _evaluate_r7(
        self,
        unit: Unit | None,
    ) -> RuleEvaluation:
        if unit is None:
            return RuleEvaluation(
                rule_id="R7",
                status=RuleStatus.FAIL,
                explanation=(
                    "The extracted unit does not exist in the owner's "
                    "property records."
                ),
                evidence=[],
            )

        if unit.status != "available":
            return RuleEvaluation(
                rule_id="R7",
                status=RuleStatus.FAIL,
                explanation=(
                    f"Unit {unit.unit_number} exists but is currently "
                    f"marked as {unit.status}."
                ),
                evidence=[],
            )

        return RuleEvaluation(
            rule_id="R7",
            status=RuleStatus.PASS,
            explanation=(
                f"Unit {unit.unit_number} exists in the owner's records "
                "and is marked available."
            ),
            evidence=[],
        )

    @staticmethod
    def _evidence_for_fields(
        lease: LeaseExtractionResult,
        field_names: set[str],
    ) -> list[EvidenceItem]:
        return [
            item
            for item in lease.evidence
            if item.field_name in field_names
        ]

    @staticmethod
    def _months_between(
        start_date: date,
        end_date: date,
    ) -> int:
        """
        Calculate the lease term in calendar months.

        Examples:
        2026-11-01 -> 2027-10-31 = 12 months
        2026-11-15 -> 2027-11-14 = 12 months
        2026-11-15 -> 2027-11-15 = 12 months
        """

        months = (
            (end_date.year - start_date.year) * 12
            + end_date.month
            - start_date.month
        )

        last_day = monthrange(
            end_date.year,
            end_date.month,
        )[1]

        # Example:
        # 2026-11-01 -> 2027-10-31
        # This is a complete 12-month lease.
        if start_date.day == 1 and end_date.day == last_day:
            return months + 1

        # Example:
        # 2026-11-15 -> 2027-11-14
        if end_date.day == start_date.day - 1:
            return months + 1

        if end_date.day < start_date.day:
            months -= 1

        return months