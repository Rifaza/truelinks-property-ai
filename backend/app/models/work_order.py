from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    issue_id: Mapped[int] = mapped_column(
        ForeignKey("property_issues.id"),
        nullable=False,
        unique=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    affected_unit: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="DRAFT",
    )

    issue: Mapped["PropertyIssue"] = relationship(
        back_populates="work_order",
    )