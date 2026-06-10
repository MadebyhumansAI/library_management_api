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
    books = book_service.update_books(db, updates)
    return [BookResponse.model_validate(b) for b in books]
