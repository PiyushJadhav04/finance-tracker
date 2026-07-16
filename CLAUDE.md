# CLAUDE.md

## Project

Expense tracker backend — see `PROJECT_PLAN.md` for the full phased plan and
current step. Always check `PROJECT_PLAN.md` for what step we're on before
starting new work.

## Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Alembic (migrations)
- Pydantic (request/response schemas)
- JWT auth (via `python-jose` or `pyjwt`), passwords hashed with `passlib[bcrypt]`
- pytest for testing

## Folder Structure

```
app/
  main.py              # FastAPI app entrypoint
  config.py            # env/config loading
  db.py                # DB session/engine setup
  models/              # SQLAlchemy models
  schemas/             # Pydantic request/response schemas
  routers/             # API route definitions
  services/            # business logic, separate from route handlers
  dependencies/        # auth dependencies, shared FastAPI dependencies
alembic/               # migrations
tests/
  unit/
  integration/
.env                    # secrets, not committed
```

## Coding Conventions

- Use `async def` route handlers and async SQLAlchemy where practical
- Keep route handlers thin — business logic goes in `services/`, not in routers
- All Pydantic schemas separate from SQLAlchemy models (don't return ORM objects directly)
- Type hints everywhere
- No bare `except:` — catch specific exceptions
- Environment variables loaded via a single `config.py`, never scattered `os.getenv` calls

## Security Rules (non-negotiable)

- Every transaction-related endpoint must scope queries to the authenticated
  user (`WHERE user_id = current_user.id`) — never trust a client-supplied user_id
- Passwords hashed with bcrypt/argon2, never stored or logged in plaintext
- JWT secret loaded from env, never hardcoded
- Validate all input via Pydantic schemas before touching the DB

## Testing Expectations

- Every new endpoint gets at least one integration test
- Auth-sensitive logic (login, token validation, data scoping) gets unit tests
- Include a test that verifies User A cannot access User B's data

## Working Style

- This is a learning project for someone new to professional software
  engineering — briefly explain non-obvious decisions (why this index, why
  this auth pattern) rather than just writing code silently
- Follow the phased plan in `PROJECT_PLAN.md` — don't skip ahead to later
  phases (CSV import, OCR, etc.) unless explicitly asked
- Prefer clarity over cleverness
