from unittest.mock import MagicMock

from app.services import book_service
from tests.helpers import make_book


def test_list_books_groups_by_genre_with_counts() -> None:
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        make_book(1, "Dune", "scifi"),
        make_book(2, "Neuromancer", "scifi"),
        make_book(3, "Hamlet", "drama"),
    ]

    groups = {g.genre: g for g in book_service.list_books_grouped_by_genre(db)}

    assert groups["scifi"].count == 2
    assert {b.title for b in groups["scifi"].books} == {"Dune", "Neuromancer"}
    assert groups["drama"].count == 1


def test_list_books_masks_18plus_titles() -> None:
    db = MagicMock()
    db.scalars.return_value.all.return_value = [make_book(1, "Secret", "18+")]

    groups = book_service.list_books_grouped_by_genre(db)

    assert groups[0].books[0].title == "***"
    # other fields stay intact
    assert groups[0].books[0].genre == "18+"
