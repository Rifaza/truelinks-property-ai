from sqlalchemy.orm import Session

from app.models import Unit


class UnitMatcher:
    """
    Matches an extracted unit number against the owner's property records.

    The matcher identifies the unit. It does not decide whether the unit
    passes R7; that decision belongs to the rules engine.
    """

    def find_unit(
        self,
        db: Session,
        unit_number: str,
    ) -> Unit | None:
        return (
            db.query(Unit)
            .filter(Unit.unit_number == unit_number)
            .first()
        )