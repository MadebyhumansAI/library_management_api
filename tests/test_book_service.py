from unittest.mock import MagicMock

import pytest

from app.exceptions import GenreNotAllowedError
from app.models import Book
from app.schemas.book import BookCreate
from app.services import book_service


def _book(id: int, title: str, genre: str) -> Book:
    return Book(id=id, title=title, author="A", publication_year=2000, genre=genre)


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


def test_list_books_groups_by_genre_with_counts() -> None:
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        _book(1, "Dune", "scifi"),
        _book(2, "Neuromancer", "scifi"),
        _book(3, "Hamlet", "drama"),
    ]

    groups = {g.genre: g for g in book_service.list_books_grouped_by_genre(db)}

    assert groups["scifi"].count == 2
    assert {b.title for b in groups["scifi"].books} == {"Dune", "Neuromancer"}
    assert groups["drama"].count == 1


def test_list_books_masks_18plus_titles() -> None:
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        _book(1, "Secret", "18+"),
    ]

    groups = book_service.list_books_grouped_by_genre(db)

    assert groups[0].books[0].title == "***"
    # other fields stay intact
    assert groups[0].books[0].genre == "18+"
