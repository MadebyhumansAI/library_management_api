from unittest.mock import MagicMock

import pytest

from app.exceptions import BookNotFoundError
from app.schemas.book import BookUpdateItem
from app.services import book_service
from tests.helpers import make_book


def test_update_multiple_books_applies_each_change() -> None:
    db = MagicMock()
    book1 = make_book(1, "Old One", "scifi")
    book2 = make_book(2, "Old Two", "scifi")
    store = {1: book1, 2: book2}
    db.get.side_effect = lambda _model, book_id: store.get(book_id)

    result = book_service.update_books(
        db,
        [
            BookUpdateItem(id=1, title="New One"),
            BookUpdateItem(id=2, genre="fantasy", publication_year=1999),
        ],
    )

    assert book1.title == "New One"
    assert book2.genre == "fantasy"
    assert book2.publication_year == 1999
    db.commit.assert_called_once()
    assert result == [book1, book2]


def test_update_only_changes_provided_fields() -> None:
    db = MagicMock()
    book = make_book(1, "Original", "scifi")  # author="A", year=2000
    db.get.return_value = book

    book_service.update_books(db, [BookUpdateItem(id=1, title="Renamed")])

    assert book.title == "Renamed"
    assert book.author == "A"  # untouched
    assert book.publication_year == 2000  # untouched


def test_update_missing_id_raises_not_found() -> None:
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(BookNotFoundError) as exc_info:
        book_service.update_books(db, [BookUpdateItem(id=99, title="Ghost")])

    assert exc_info.value.book_id == 99


def test_update_is_atomic_when_any_id_missing() -> None:
    db = MagicMock()
    book1 = make_book(1, "Real", "scifi")
    store = {1: book1}
    db.get.side_effect = lambda _model, book_id: store.get(book_id)

    with pytest.raises(BookNotFoundError):
        book_service.update_books(
            db,
            [
                BookUpdateItem(id=1, title="Changed"),
                BookUpdateItem(id=99, title="Ghost"),
            ],
        )

    db.commit.assert_not_called()
