# app/schemas/book.py
from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    publication_year: int = Field(..., ge=1000, le=2100)
    genre: str = Field(..., min_length=1, max_length=50)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(None, min_length=1, max_length=200)
    author: str | None = None
    publication_year: int | None = Field(None, ge=1000, le=2100)
    genre: str | None = None


class BookUpdateItem(BookUpdate):
    id: int


class BookResponse(BookBase):
    id: int


class GenreGroup(BaseModel):
    genre: str
    count: int
    books: list[BookResponse]
