import pytest
from conftest import create_test_user
from httpx import AsyncClient


# test user register
@pytest.mark.anyio
async def test_user_register(client: AsyncClient):

    username: str = "testuser"
    email: str = "testuser@gmail.com"
    password: str = "testpass1234"

    response = await client.post(
        "/user/api/register",
        json={"username": username, "email": email, "password": password},
    )

    assert response.status_code == 201


# test user already exist
@pytest.mark.anyio
async def test_user_already_exist(client: AsyncClient):

    # a user is created
    await create_test_user(client)

    # again
    username: str = "testuser"
    email: str = "test@gmail.com"
    password: str = "testpass123"

    response = await client.post(
        "/user/api/register",
        json={"username": username, "email": email, "password": password},
    )

    assert response.status_code == 409


# test for login of user
@pytest.mark.anyio
async def test_login_for_user(client: AsyncClient):

    # save a dummy user in database (register)
    await create_test_user(client)

    # send a response to login with same username and password
    # check it response token is same as register token

    response = await client.post(
        "/user/api/login", data={"username": "testuser", "password": "testpass123"}
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"].lower() == "bearer"

    assert len(response_data["access_token"]) > 0
