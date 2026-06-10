from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import BookNotFoundError, GenreNotAllowedError
from app.models import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdateItem, GenreGroup

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

    # container for grouping books by genre
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


def update_books(db: Session, updates: list[BookUpdateItem]) -> list[Book]:
    books = []
    for change in updates:
        book = db.get(Book, change.id)
        if book is None:
            raise BookNotFoundError(change.id)
        fields = change.model_dump(exclude_unset=True, exclude={"id"})
        for name, value in fields.items():
            setattr(book, name, value)
        books.append(book)

    db.commit()
    for book in books:
        db.refresh(book)
    return books
