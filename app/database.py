# app/database.py
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SQLITE_URL = "sqlite:///./books.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session]:
    """
    Yields a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
