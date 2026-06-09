from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import GenreNotAllowedError
from app.models import Book
from app.schemas.book import BookCreate, BookResponse, GenreGroup

BLOCKED_GENRES = {"horror"}
MASKED_GENRES = {"18+"}
MASKED_TITLE = "***"


def create_book(db: Session, data: BookCreate) -> Book:
    if data.genre.lower() in BLOCKED_GENRES:
        raise GenreNotAllowedError(data.genre)
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def list_books_grouped_by_genre(db: Session) -> list[GenreGroup]:
    books = db.scalars(select(Book)).all()

    grouped: dict[str, list[BookResponse]] = defaultdict(list)
    for book in books:
        item = BookResponse.model_validate(book)
        if book.genre.lower() in MASKED_GENRES:
            item = item.model_copy(update={"title": MASKED_TITLE})
        grouped[book.genre].append(item)

    return [
        GenreGroup(genre=genre, count=len(items), books=items)
        for genre, items in grouped.items()
    ]
