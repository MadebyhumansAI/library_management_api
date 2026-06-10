from app.models import Book


def make_book(id: int, title: str = "Dune", genre: str = "scifi") -> Book:
    """Build Book with defaults for tests."""
    return Book(id=id, title=title, author="A", publication_year=2000, genre=genre)
