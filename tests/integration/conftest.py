import asyncpg
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base
from app.config import settings

TEST_DB_NAME = "receipt_tracker_test"
TEST_DATABASE_URL = settings.DATABASE_URL.replace(f"/{settings.POSTGRES_DB}", f"/{TEST_DB_NAME}")


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    raw_conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database="postgres",
    )
    try:
        await raw_conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    finally:
        await raw_conn.close()

    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine):
    session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.services.s3.s3_service.init_bucket", new_callable=AsyncMock):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    app.dependency_overrides.clear()
