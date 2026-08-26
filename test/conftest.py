# 1. set envrionment to dummy database
import os
from collections.abc import AsyncGenerator

os.environ["DB_URL"] = "postgresql+psycopg://postgres:sahil@localhost/test_db"
os.environ["SECRET_KEY"] = "this_is_a_dummy_secrete_key_for_sha_256"

# 2. fixtues
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.dependencies import get_db
from app.db import Base
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# b. create async engine
@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(url=os.environ["DB_URL"], poolclass=NullPool)

    return engine


# c. create setup database
@pytest.fixture(scope="session")
async def setup_database(test_engine):

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


# d. create async db session
@pytest.fixture
async def db_session(test_engine, setup_database):

    conn = await test_engine.connect()
    trann = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = test_async_session()
    try:
        yield session
    finally:
        await session.close()
        await trann.rollback()
        await conn.close()


# e. create client
@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# 3. helper
from pydantic import EmailStr


# a. register helper
async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: EmailStr = "test@gmail.com",
    password: str = "testpass123",
):

    response = await client.post(
        "/user/api/register",
        json={"username": username, "email": email, "password": password},
    )

    assert response.status_code == 201, f"Failed to create user {response.text}"
    return response.json()


# b. login helper
async def login_test_user(
    client: AsyncClient, username: str = "testuser", password: str = "testpass123"
):

    response = await client.post(
        "/user/api/login", data={"username": username, "password": password}
    )

    assert response.status_code == 200, f"Failed to login user {response.text}"
    return response.json()["access_token"]


# c. header helper
def async_header(token: str):
    return {"Authorization": f"Bearer {token}"}
