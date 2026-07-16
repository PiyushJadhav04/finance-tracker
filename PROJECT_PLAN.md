# Expense Tracker — Project Plan

## Overview

A personal expense tracker built to learn: backend fundamentals, database design, authentication, and system design. Long-term this will grow into a ledger-style app with CSV import and receipt-photo OCR, but **Phase 1 is manual entry only.**

This is a learning project — prioritize correctness and clean structure over
speed. Explain tradeoffs when they come up (e.g., why a certain index, why a
certain auth approach).

## Stack

- **Backend**: Python + FastAPI
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Auth**: JWT-based (bcrypt/argon2 for password hashing)
- **Testing**: pytest
- **Frontend**: minimal React app

## Current Phase: Phase 1 — Manual Entry

### Step 0: Project setup

- Initialize FastAPI project structure (routers, models, schemas, services, config)
- Set up `.env` for secrets (DB connection string, JWT secret) — never commit this
- Get Postgres running locally (Docker preferred for reproducibility)
- Confirm a basic `/health` endpoint runs

### Step 1: Database schema design

Tables:

- `users`: id, email (unique), password_hash, created_at
- `transactions`: id, user_id (FK), amount, category, description, date, created_at, updated_at
- `categories`: id, name, user_id (nullable if global/default categories exist)

Constraints to enforce:

- `amount` not null
- Foreign keys enforced (transactions.user_id -> users.id)
- Index on `transactions.user_id` and `transactions.date` (queried often)

### Step 2: Migrations

- Set up Alembic
- Write initial migration creating the tables from Step 1
- Verify tables exist after running migration

### Step 3: Auth — signup & login

- `POST /auth/signup`: validate email/password, hash password, create user
- `POST /auth/login`: verify password, issue JWT
- Auth dependency/middleware: extract user from JWT, reject if missing/invalid
- Test thoroughly before moving to Step 4 — everything downstream depends on this

### Step 4: Core CRUD for transactions

- `POST /transactions` — create (tied to logged-in user)
- `GET /transactions` — list (paginated, scoped to logged-in user)
- `GET /transactions/{id}` — get one (must belong to requesting user)
- `PUT /transactions/{id}` — edit
- `DELETE /transactions/{id}` — delete
- **Critical**: every endpoint must verify the transaction belongs to the
  requesting user. This is the most common place to introduce a security bug.

### Step 5: Validation & error handling

- Reject invalid amounts, missing fields, malformed dates
- Consistent error response shape (status code + message)

### Step 6: Aggregation endpoints

- `GET /summary` — total spend this month, spend by category
- Practice SQL aggregation (GROUP BY, SUM) via SQLAlchemy

### Step 7: Tests

- Unit tests: password hashing, JWT validation
- Integration tests: create → fetch → verify correctness, and verify
  user A cannot see/edit/delete user B's transactions

### Step 8: Minimal frontend (optional)

- Simple form-based UI to log in and view/add transactions
- Not the focus — just enough to click through and sanity-check behavior

### Step 9: Wrap-up

- README explaining what it does and how to run it
- Keep `CLAUDE.md` up to date as conventions solidify

## Future Phases (not now — for context only)

- Phase 2: CSV import (bank statement upload, parsing, dedup)
- Phase 3: Receipt photo upload + OCR (blob storage, async job queue)
- Phase 4 (stretch): Bank sync via Plaid (OAuth, webhooks)

## Working Style Preferences

- Work step by step — don't jump ahead to later steps before earlier ones are solid
- Write tests alongside each feature, not as an afterthought
- Explain non-obvious decisions briefly (e.g., why bcrypt over plain hashing,
  why an index here) since this is a learning project
- Flag security-relevant choices explicitly (auth, data scoping, input validation)
- Continiously teach me things that I should know, the project is to learn and NOT simply just get it over with as fast as possible
