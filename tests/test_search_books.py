from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, Book
from app.services import book_service


@pytest.fixture
def db() -> Generator[Session]:
    """SQLite session to test SQL filters"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _add(db: Session, title: str, author: str, genre: str) -> None:
    db.add(Book(title=title, author=author, publication_year=2000, genre=genre))


def test_search_matches_title_case_insensitively(db: Session) -> None:
    _add(db, "Dune", "Frank Herbert", "scifi")
    _add(db, "Dune Messiah", "Frank Herbert", "scifi")
    _add(db, "Hamlet", "Shakespeare", "drama")
    db.commit()

    results = book_service.search_books(db, "dune")

    assert {b.title for b in results} == {"Dune", "Dune Messiah"}


def test_search_matches_author(db: Session) -> None:
    _add(db, "Dune", "Frank Herbert", "scifi")
    _add(db, "Hamlet", "Shakespeare", "drama")
    db.commit()

    results = book_service.search_books(db, "herbert")

    assert {b.title for b in results} == {"Dune"}


def test_search_excludes_18plus_books(db: Session) -> None:
    _add(db, "Secret Garden", "Burnett", "classic")
    _add(db, "Secret Diary", "Anon", "18+")  # matches "secret" but is 18+
    db.commit()

    results = book_service.search_books(db, "secret")

    assert {b.title for b in results} == {"Secret Garden"}
