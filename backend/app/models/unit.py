from __future__ import annotations

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Unit(Base):
    """
    Represents a property unit from the owner's unit records.

    Unit information is used by the unit matcher and lease validation
    rules, especially R7, which verifies that the leased unit exists
    and is marked as available.
    """

    __tablename__ = "units"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Owner's unique property identifier.
    property_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Property name from the owner's unit data.
    property_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Property location from the owner's unit data.
    location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Owner's building identifier.
    building_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Building name, for example "Tower A" or "Tower B".
    building_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Owner's unique unit identifier, for example "MC-B-1204".
    unit_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    # Human-readable unit label, for example "Apartment 1204".
    label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Unit type, for example "1BR", "2BR", or "3BR".
    unit_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Unit area in square meters.
    area_sqm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Parking bay assigned to the unit.
    parking_bay: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Owner-provided status used by R7.
    # Expected values from unit.json: "available" or "occupied".
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # A unit can have multiple leases over time.
    leases: Mapped[list["Lease"]] = relationship(
        back_populates="unit",
    )

    issues: Mapped[list["PropertyIssue"]] = relationship(
        back_populates="unit",
    )