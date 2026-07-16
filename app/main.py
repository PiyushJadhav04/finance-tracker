from fastapi import FastAPI

from app.routers import auth, transactions

app = FastAPI(title="Finance Tracker")

app.include_router(auth.router)
app.include_router(transactions.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
