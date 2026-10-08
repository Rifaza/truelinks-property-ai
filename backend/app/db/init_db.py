from app.db.database import Base, engine
import app.models

def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("DATABASE TABLES CREATED")