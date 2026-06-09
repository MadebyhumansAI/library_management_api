from fastapi import FastAPI

app = FastAPI(title="Library Management API CRUD")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
