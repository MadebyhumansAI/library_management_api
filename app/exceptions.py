class DomainError(Exception):
    """Base for business-rule violations."""

    status_code = 400


class GenreNotAllowedError(DomainError):
    def __init__(self, genre: str) -> None:
        self.genre = genre
        super().__init__(f"Cannot add new books in the {genre} genre.")


class BookNotFoundError(DomainError):
    status_code = 404

    def __init__(self, book_id: int) -> None:
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} not found.")


class LastBookInGenreError(DomainError):
    status_code = 409  # Conflict

    def __init__(self, genre: str) -> None:
        self.genre = genre
        super().__init__(f"Cannot delete the last remaining book in the {genre} genre.")
