from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.book import BookCreate, BookResponse, BookUpdateItem, GenreGroup
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)) -> BookResponse:
    created = book_service.create_book(db, book)
    return BookResponse.model_validate(created)


@router.get("/")
def list_books(db: Session = Depends(get_db)) -> list[GenreGroup]:
    return book_service.list_books_grouped_by_genre(db)


@router.patch("/")
def update_books(
    updates: list[BookUpdateItem], db: Session = Depends(get_db)
) -> list[BookResponse]:
    """Update one or many books in a single request.

    The body is a JSON list where each item is identified by its ``id`` and
    carries only the fields to change, e.g.::

        [
            {"id": 1, "title": "Dune (Revised)"},
            {"id": 2, "genre": "fantasy", "publication_year": 1999}
        ]

    Fields that are omitted from an item are left untouched (partial update).

    The batch is atomic: if any ``id`` does not exist, the whole request is
    rejected with 404 and no book is modified.
    """
    books = book_service.update_books(db, updates)
    return [BookResponse.model_validate(b) for b in books]


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    book_service.delete_book(db, book_id)


# Search books by title or author (case-insensitive, partial match).
# Books in the "18+" genre are never returned.
@router.get("/search")
def search_books(q: str, db: Session = Depends(get_db)) -> list[BookResponse]:
    books = book_service.search_books(db, q)
    return [BookResponse.model_validate(b) for b in books]
