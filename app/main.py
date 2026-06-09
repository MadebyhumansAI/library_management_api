from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import DomainError
from app.routes import books

app = FastAPI(title="Library Management API")


@app.exception_handler(DomainError)
def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(books.router)
