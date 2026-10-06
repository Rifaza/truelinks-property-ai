from app.db.database import Base, engine
from app.models import Evidence, Lease, Unit


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("DATABASE TABLES CREATED")