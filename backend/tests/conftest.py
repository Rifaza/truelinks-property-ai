import pytest

from app.db.database import Base, SessionLocal, engine


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()