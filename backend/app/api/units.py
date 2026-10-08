from fastapi import APIRouter, HTTPException

from app.db.database import SessionLocal
from app.models.unit import Unit
from app.schemas.unit_overview import (
    IssueOverview,
    LeaseOverview,
    UnitOverviewResponse,
    WorkOrderOverview,
)


router = APIRouter(
    prefix="/api/units",
    tags=["Units"],
)


@router.get(
    "/{unit_id}",
    response_model=UnitOverviewResponse,
)
def get_unit_overview(unit_id: int) -> UnitOverviewResponse:
    db = SessionLocal()

    try:
        unit = db.get(Unit, unit_id)

        if unit is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unit with id {unit_id} not found.",
            )

        lease = None

        if unit.leases:
            current_lease = unit.leases[-1]

            lease = LeaseOverview(
                id=current_lease.id,
                tenant_name=current_lease.tenant_name,
                monthly_rent=current_lease.monthly_rent,
                annual_rent=current_lease.annual_rent,
                deposit_amount=current_lease.deposit_amount,
                start_date=current_lease.start_date,
                end_date=current_lease.end_date,
                term_months=current_lease.term_months,
            )

        issues = []

        for issue in unit.issues:
            work_order = None

            if issue.work_order:
                work_order = WorkOrderOverview(
                    id=issue.work_order.id,
                    title=issue.work_order.title,
                    description=issue.work_order.description,
                    affected_unit=issue.work_order.affected_unit,
                    recommended_action=issue.work_order.recommended_action,
                    status=issue.work_order.status,
                )

            issues.append(
                IssueOverview(
                    id=issue.id,
                    issue=issue.issue,
                    description=issue.description,
                    severity=issue.severity,
                    condition=issue.condition,
                    visible_items=(
                        issue.visible_items.split(", ")
                        if issue.visible_items
                        else []
                    ),
                    status=issue.status,
                    work_order=work_order,
                )
            )

        return UnitOverviewResponse(
            id=unit.id,
            unit_number=unit.unit_number,
            label=unit.label,
            unit_type=unit.unit_type,
            area_sqm=unit.area_sqm,
            parking_bay=unit.parking_bay,
            status=unit.status,
            lease=lease,
            issues=issues,
        )

    finally:
        db.close()