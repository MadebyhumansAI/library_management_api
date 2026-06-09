from sqlalchemy.orm import Session

from app.exceptions import GenreNotAllowedError
from app.models import Book
from app.schemas.book import BookCreate

BLOCKED_GENRES = {"horror"}


def create_book(db: Session, data: BookCreate) -> Book:
    if data.genre.lower() in BLOCKED_GENRES:
        raise GenreNotAllowedError(data.genre)
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book
