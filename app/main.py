from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.exceptions import DomainError
from app.routes import books

app = FastAPI(title="Library Management API")


@app.exception_handler(DomainError)
def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


app.include_router(books.router)
