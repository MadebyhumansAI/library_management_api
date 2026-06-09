class DomainError(Exception):
    """Base for business-rule violations."""


class GenreNotAllowedError(DomainError):
    def __init__(self, genre: str) -> None:
        self.genre = genre
        super().__init__(f"Cannot add new books in the {genre} genre.")
