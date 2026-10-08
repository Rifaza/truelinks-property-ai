from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class PropertyIssue(Base):
    __tablename__ = "property_issues"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    unit_id: Mapped[int] = mapped_column(
        ForeignKey("units.id"),
        nullable=False,
    )

    issue: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    condition: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    visible_items: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="OPEN",
    )

    unit: Mapped["Unit"] = relationship(
        back_populates="issues",
    )

    work_order: Mapped["WorkOrder | None"] = relationship(
        back_populates="issue",
        uselist=False,
        cascade="all, delete-orphan",
    )