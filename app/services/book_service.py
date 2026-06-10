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
    """Create and persist a new book.

    Args:
        db: Active database session.
        data: Validated payload describing the book to create.

    Returns:
        The persisted ``Book``, refreshed with its generated ``id``.

    Raises:
        GenreNotAllowedError: If the book's genre is blocked (``horror``).
    """
    if data.genre.lower() in BLOCKED_GENRES:
        raise GenreNotAllowedError(data.genre)
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def list_books_grouped_by_genre(db: Session) -> list[GenreGroup]:
    """List all books grouped by genre, with a per-genre count.

    Titles of books in a masked genre (e.g. ``18+``) are replaced with a
    placeholder in the response; the stored records are not modified.

    Args:
        db: Active database session.

    Returns:
        One ``GenreGroup`` per genre, each holding the genre name, the number
        of books in it, and the (possibly masked) books themselves.
    """
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
    """Apply partial updates to one or many books in a single transaction.

    Each item is matched by its ``id`` and only the fields it sets are changed;
    omitted fields are left untouched. The operation is atomic: if any ``id``
    is missing, nothing is committed.

    Args:
        db: Active database session.
        updates: Update items, each carrying an ``id`` plus the fields to change.

    Returns:
        The updated ``Book`` records, in the order they were given.

    Raises:
        BookNotFoundError: If any ``id`` does not match an existing book.
    """
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
    """Delete a book by id, unless it is the last one in its genre.

    Args:
        db: Active database session.
        book_id: Identifier of the book to delete.

    Raises:
        BookNotFoundError: If no book exists with the given id.
        LastBookInGenreError: If the book is the only one left in its genre.
    """
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
    """Search books by title or author.

    The query is matched case-insensitively as a substring against both the
    title and the author. Books in an unsearchable genre (e.g. ``18+``) are
    never returned.

    Args:
        db: Active database session.
        query: Free-text term to match against title and author.

    Returns:
        The matching books, excluding any in an unsearchable genre.
    """
    pattern = f"%{query}%"
    stmt = (
        select(Book)
        .where(or_(Book.title.ilike(pattern), Book.author.ilike(pattern)))
        .where(Book.genre.not_in(UNSEARCHABLE_GENRES))
    )
    return list(db.scalars(stmt).all())
