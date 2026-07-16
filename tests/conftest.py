import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401  (registers models on Base.metadata)
from app.config import settings
from app.db import Base, get_db
from app.main import app


async def _create_schema() -> None:
    engine = create_async_engine(settings.test_database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _drop_schema() -> None:
    engine = create_async_engine(settings.test_database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _test_schema():
    # Run outside pytest-asyncio's per-test event loop (via asyncio.run)
    # since this fixture is session-scoped but each test function gets its
    # own event loop by default — sharing one asyncpg engine/connection
    # across those loops causes "attached to a different loop" errors.
    asyncio.run(_create_schema())
    yield
    asyncio.run(_drop_schema())


@pytest_asyncio.fixture
async def db_session():
    # A fresh engine per test keeps its connections scoped to this test's
    # event loop, for the same reason as above.
    engine = create_async_engine(settings.test_database_url)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client):
    await client.post(
        "/auth/signup", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    login = await client.post(
        "/auth/login", data={"username": "alice@example.com", "password": "supersecret123"}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
