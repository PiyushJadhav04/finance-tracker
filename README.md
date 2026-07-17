# Finance Tracker

A personal expense tracker with a FastAPI backend and a minimal React
frontend. Built as a learning project — see `PROJECT_PLAN.md` for the phased
build plan and `CLAUDE.md` for coding conventions.

Built to get more familiar with claude code.

## Stack

- **Backend**: FastAPI, SQLAlchemy (async), Alembic, PostgreSQL
- **Auth**: JWT (python-jose), passwords hashed with bcrypt (passlib)
- **Testing**: pytest, pytest-asyncio, httpx
- **Frontend**: React + Vite (plain JS, no router — just enough to click
  through manually)

## Prerequisites

- Python 3.11+
- Node 20+
- Docker (for Postgres)

## Setup

1. **Copy the env file and fill in real values:**

   ```bash
   cp .env.example .env
   ```

   `DATABASE_URL` and `TEST_DATABASE_URL` point at the dev and test Postgres
   databases respectively; `JWT_SECRET` should be a long random string (e.g.
   `python -c "import secrets; print(secrets.token_hex(32))"`). Never commit
   `.env`.

2. **Start Postgres:**

   ```bash
   docker compose up -d
   ```

3. **Create a Python virtualenv and install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Create the test database** (one-time; the app database is created
   automatically by `docker-compose.yml`):

   ```bash
   docker compose exec db psql -U finance_tracker -d finance_tracker \
     -c "CREATE DATABASE finance_tracker_test;"
   ```

5. **Run migrations:**

   ```bash
   alembic upgrade head
   ```

## Running the backend

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at http://localhost:5173. The backend must be running for the
frontend to work — it calls the API directly (CORS is configured to allow
this origin).

## Running tests

```bash
source venv/bin/activate
pytest
```

Tests run against `finance_tracker_test` (created in setup step 4), never
against the dev database. Each test gets a clean, isolated session.

## API overview

All endpoints except `/health`, `/auth/signup`, and `/auth/login` require a
JWT bearer token (obtained from `/auth/login`) in the `Authorization` header.

| Method | Path                 | Description                                 |
| ------ | -------------------- | ------------------------------------------- |
| GET    | `/health`            | Liveness check                              |
| POST   | `/auth/signup`       | Create a user                               |
| POST   | `/auth/login`        | Log in, returns a JWT (OAuth2 form body)    |
| GET    | `/auth/me`           | Current authenticated user                  |
| POST   | `/transactions`      | Create a transaction                        |
| GET    | `/transactions`      | List your transactions (paginated)          |
| GET    | `/transactions/{id}` | Get one transaction                         |
| PUT    | `/transactions/{id}` | Partially update a transaction              |
| DELETE | `/transactions/{id}` | Delete a transaction                        |
| GET    | `/summary`           | Total spend + spend by category for a month |

Every transaction/summary endpoint is scoped to the authenticated user —
there is no way to read or modify another user's data.

## Project structure

```
app/
  main.py              # FastAPI app entrypoint, CORS, exception handlers
  config.py             # env/config loading (single source of truth)
  db.py                 # async SQLAlchemy engine/session setup
  models/                # SQLAlchemy models (users, categories, transactions)
  schemas/                # Pydantic request/response schemas
  routers/                 # API route definitions
  services/                 # business logic, DB queries
  dependencies/              # auth dependency (JWT -> current user)
alembic/                      # migrations
tests/
  unit/                        # pure-function tests (hashing, JWT)
  integration/                   # API-level tests against a real test DB
frontend/                        # minimal React app
```
