from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.exception_handlers import validation_exception_handler
from app.routers import auth, transactions

app = FastAPI(title="Finance Tracker")

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth.router)
app.include_router(transactions.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
