from collections import defaultdict

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.exceptions import (
    BookNotFoundError,
    GenreNotAllowedError,
    LastBookInGenreError,
)
from app.models import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdateItem, GenreGroup

BLOCKED_GENRES = {"horror"}
MASKED_GENRES = {"18+"}
MASKED_TITLE = "***"
UNSEARCHABLE_GENRES = {"18+"}


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


def delete_book(db: Session, book_id: int) -> None:
    book = db.get(Book, book_id)
    if book is None:
        raise BookNotFoundError(book_id)

    genre_count = db.scalar(
        select(func.count()).select_from(Book).where(Book.genre == book.genre)
    )
    if (genre_count or 0) <= 1:
        raise LastBookInGenreError(book.genre)

    db.delete(book)
    db.commit()


def search_books(db: Session, query: str) -> list[Book]:
    pattern = f"%{query}%"
    stmt = (
        select(Book)
        .where(or_(Book.title.ilike(pattern), Book.author.ilike(pattern)))
        .where(Book.genre.not_in(UNSEARCHABLE_GENRES))
    )
    return list(db.scalars(stmt).all())
