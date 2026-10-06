from app.db.database import SessionLocal
from app.models import Unit


def seed_units() -> None:
    db = SessionLocal()

    try:
        # Avoid duplicate records if the seed script is run more than once.
        existing_count = db.query(Unit).count()

        if existing_count > 0:
            print(f"UNITS ALREADY SEEDED: {existing_count}")
            return

        units = [
            Unit(
                property_id="PROP-MC",
                property_name="Marina Crest Residences",
                location="Lusail Marina District, Doha",
                building_id="MC-B",
                building_name="Tower B",
                unit_number="MC-B-1204",
                label="Apartment 1204",
                unit_type="2BR",
                area_sqm=118,
                parking_bay="B-77",
                status="available",
            ),
            Unit(
                property_id="PROP-MC",
                property_name="Marina Crest Residences",
                location="Lusail Marina District, Doha",
                building_id="MC-B",
                building_name="Tower B",
                unit_number="MC-B-1205",
                label="Apartment 1205",
                unit_type="2BR",
                area_sqm=121,
                parking_bay="B-78",
                status="occupied",
            ),
            Unit(
                property_id="PROP-MC",
                property_name="Marina Crest Residences",
                location="Lusail Marina District, Doha",
                building_id="MC-B",
                building_name="Tower B",
                unit_number="MC-B-0902",
                label="Apartment 0902",
                unit_type="1BR",
                area_sqm=74,
                parking_bay="B-51",
                status="available",
            ),
            Unit(
                property_id="PROP-MC",
                property_name="Marina Crest Residences",
                location="Lusail Marina District, Doha",
                building_id="MC-A",
                building_name="Tower A",
                unit_number="MC-A-0301",
                label="Apartment 0301",
                unit_type="3BR",
                area_sqm=156,
                parking_bay="A-12",
                status="available",
            ),
            Unit(
                property_id="PROP-MC",
                property_name="Marina Crest Residences",
                location="Lusail Marina District, Doha",
                building_id="MC-A",
                building_name="Tower A",
                unit_number="MC-A-0302",
                label="Apartment 0302",
                unit_type="3BR",
                area_sqm=156,
                parking_bay="A-13",
                status="occupied",
            ),
        ]

        db.add_all(units)
        db.commit()

        print(f"SEEDED {len(units)} UNITS SUCCESSFULLY")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_units()