from app.db.database import SessionLocal
from app.services.unit_matcher import UnitMatcher


def test_unit_matcher_finds_existing_unit():
    db = SessionLocal()

    try:
        matcher = UnitMatcher()

        unit = matcher.find_unit(
            db,
            "MC-B-1204",
        )

        assert unit is not None
        assert unit.unit_number == "MC-B-1204"
        assert unit.status == "available"

    finally:
        db.close()


def test_unit_matcher_returns_none_for_unknown_unit():
    db = SessionLocal()

    try:
        matcher = UnitMatcher()

        unit = matcher.find_unit(
            db,
            "UNKNOWN-UNIT",
        )

        assert unit is None

    finally:
        db.close()