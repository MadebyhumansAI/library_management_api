from unittest.mock import MagicMock

import pytest

from app.exceptions import BookNotFoundError, LastBookInGenreError
from app.services import book_service
from tests.helpers import make_book


def test_delete_book_removes_when_genre_has_others() -> None:
    db = MagicMock()
    book = make_book(1, "Dune", "scifi")
    db.get.return_value = book
    db.scalar.return_value = 2  # genre still has another book

    book_service.delete_book(db, 1)

    db.delete.assert_called_once_with(book)
    db.commit.assert_called_once()


def test_delete_last_book_in_genre_raises() -> None:
    db = MagicMock()
    book = make_book(1, "Dune", "scifi")
    db.get.return_value = book
    db.scalar.return_value = 1  # the only book in its genre

    with pytest.raises(LastBookInGenreError) as exc_info:
        book_service.delete_book(db, 1)

    assert exc_info.value.genre == "scifi"
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_missing_id_raises_not_found() -> None:
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(BookNotFoundError):
        book_service.delete_book(db, 99)

    db.delete.assert_not_called()
    db.commit.assert_not_called()
