from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.book import BookCreate, BookResponse
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)) -> BookResponse:
    created = book_service.create_book(db, book)
    return BookResponse.model_validate(created)
