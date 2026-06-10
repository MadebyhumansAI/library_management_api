from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import DomainError
from app.routes import books

app = FastAPI(title="Library Management API")


@app.exception_handler(DomainError)
def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


app.include_router(books.router)
