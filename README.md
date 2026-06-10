# Library Management API

A small FastAPI service for managing a library of books. Full CRUD
plus search, organised in a layered structure:

- **routes** ([app/routes](app/routes)) — HTTP only (parse request, return response)
- **services** ([app/services](app/services)) — business rules + persistence
- **schemas** ([app/schemas](app/schemas)) — Pydantic request/response models
- **models** ([app/models](app/models)) — SQLAlchemy ORM tables
- **exceptions** ([app/exceptions.py](app/exceptions.py)) — domain errors mapped to HTTP codes

## Requirements

- Python 3.13 (see [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Setup

Clone the repository:

```bash
git clone git@github.com:MadebyhumansAI/library_management_api.git
cd library_management_api
```

Install all dependencies (app + dev) into a local `.venv`:

```bash
uv sync
```

> `uv sync` reads [pyproject.toml](pyproject.toml) and [uv.lock](uv.lock) and creates
> a reproducible environment. Run any project command with `uv run <cmd>` so it
> uses that environment — you do not need to activate the venv manually.

## Database migrations

Migrations are managed with [Alembic](https://alembic.sqlalchemy.org/). The
config ([alembic/env.py](alembic/env.py)) reads the database URL from
[app/database.py](app/database.py) and uses the models' metadata, so
`--autogenerate` detects model changes automatically.

Apply all existing migrations (also how you initialise a fresh database):

```bash
uv run alembic upgrade head
```

Other useful commands:

```bash
uv run alembic current        # show the current revision
uv run alembic history        # list all revisions
uv run alembic downgrade -1   # roll back the most recent migration
```

### Example: add a column, then remove it

**1. Add a column to the model.** In [app/models/book.py](app/models/book.py), add a
field to the `Book` class:

```python
summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

**2. Generate and apply the migration:**

```bash
uv run alembic revision --autogenerate -m "add summary to books"
uv run alembic upgrade head
```

Alembic compares the model against the database and writes a new file under
[alembic/versions/](alembic/versions/) containing `op.add_column(...)`. Review it,
then `upgrade head` applies it.

**3. Remove the column again.** Delete the `summary` line from the model, then:

```bash
uv run alembic revision --autogenerate -m "remove summary from books"
uv run alembic upgrade head
```

This produces a migration with `op.drop_column("books", "summary")`.

> Always open the generated file before running `upgrade` — autogenerate is a
> good first draft, not a guarantee (it does not detect every change, e.g. some
> renames or server defaults).

## Seed sample data

Load 10 example books (including `Horror` and `18+` titles, handy for trying the
genre rules). Run the schema migration first, then, from the project root:

```bash
uv run python seeds/seed.py
```

## Run the app

```bash
uv run uvicorn app.main:app --reload
```

- API root: http://127.0.0.1:8000/
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

The app uses a local SQLite database (`books.db`). Create the schema with a
migration before first use (see [Database migrations](#database-migrations)).


## Run the tests

```bash
uv run pytest
```

Tests live in [tests/](tests/), split by operation (`test_create_book.py`,
`test_read_books.py`, `test_update_books.py`, `test_delete_book.py`,
`test_search_books.py`). Service logic is unit-tested with a mocked DB session;
search uses a real in-memory SQLite database so the SQL filter is exercised.

## Endpoints

| Method   | Path                  | Description                                            |
| -------- | --------------------- | ------------------------------------------------------ |
| `POST`   | `/books/`             | Create a book (the `horror` genre is rejected).        |
| `GET`    | `/books/`             | List books grouped by genre with counts; `18+` titles are masked. |
| `PATCH`  | `/books/`             | Update one or many books at once (partial, atomic).    |
| `DELETE` | `/books/{book_id}`    | Delete a book; the last book in a genre cannot be deleted. |
| `GET`    | `/books/search?q=...` | Search by title or author; `18+` books are excluded.   |


## Code quality & pre-commit

Quality checks run automatically on every commit via
[pre-commit](https://pre-commit.com/) ([.pre-commit-config.yaml](.pre-commit-config.yaml)).
The git hook is already configured; if you clone fresh, install it once:

```bash
uv run pre-commit install
```

Run all checks against the whole repo at any time:

```bash
uv run pre-commit run --all-files
```

### What runs on commit

| Tool                  | Purpose                                                         |
| --------------------- | -------------------------------------------------------------- |
| **ruff** (`--fix`)    | Linting (pyflakes, pycodestyle, import sorting, pyupgrade).     |
| **ruff-format**       | Code formatting (88-char line length).                         |
| **mypy** (`--strict`) | Static type checking of the `app/` package.                    |
| **bandit**            | Security linter — flags common insecure code patterns.         |
| pre-commit-hooks      | Trailing whitespace, end-of-file, YAML/TOML validity, large files, merge conflicts. |

### Dependency vulnerability scanning (manual)

[safety](https://pypi.org/project/safety/) checks installed dependencies against
a database of known vulnerabilities. It is part of the dev dependencies but not
wired into pre-commit; run it on demand:

```bash
uv run safety scan
```
