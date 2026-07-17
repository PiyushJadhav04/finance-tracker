from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.exception_handlers import validation_exception_handler
from app.routers import auth, summary, transactions

app = FastAPI(title="Finance Tracker")

app.add_exception_handler(RequestValidationError, validation_exception_handler)

# local frontend dev server only — browsers block cross-origin requests by
# default, so without this the React app on :5173 couldn't call this API on :8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(summary.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
