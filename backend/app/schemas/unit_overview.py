from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class LeaseOverview(BaseModel):
    id: int
    tenant_name: str | None
    monthly_rent: Decimal | None
    annual_rent: Decimal | None
    deposit_amount: Decimal | None
    start_date: date | None
    end_date: date | None
    term_months: int | None


class WorkOrderOverview(BaseModel):
    id: int
    title: str
    description: str
    affected_unit: str
    recommended_action: str
    status: str


class IssueOverview(BaseModel):
    id: int
    issue: str
    description: str
    severity: str
    condition: str
    visible_items: list[str] = Field(default_factory=list)
    status: str
    work_order: WorkOrderOverview | None = None


class UnitOverviewResponse(BaseModel):
    id: int
    unit_number: str
    label: str
    unit_type: str
    area_sqm: Decimal
    parking_bay: str | None
    status: str
    lease: LeaseOverview | None
    issues: list[IssueOverview] = Field(default_factory=list)