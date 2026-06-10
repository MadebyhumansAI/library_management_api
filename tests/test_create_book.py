from unittest.mock import MagicMock

import pytest

from app.exceptions import GenreNotAllowedError
from app.schemas.book import BookCreate
from app.services import book_service


def test_create_book_persists_and_returns_a_book() -> None:
    db = MagicMock()
    data = BookCreate(
        title="Dune", author="Frank Herbert", publication_year=1965, genre="scifi"
    )

    result = book_service.create_book(db, data)

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    assert result.title == "Dune"
    assert result.genre == "scifi"


def test_create_book_rejects_horror_genre() -> None:
    db = MagicMock()
    data = BookCreate(
        title="It", author="Stephen King", publication_year=1986, genre="Horror"
    )

    with pytest.raises(GenreNotAllowedError):
        book_service.create_book(db, data)

    db.add.assert_not_called()
    db.commit.assert_not_called()
