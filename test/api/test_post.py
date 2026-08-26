import pytest
from conftest import async_header, create_test_user, login_test_user
from httpx import AsyncClient


# when there is no post
@pytest.mark.anyio
async def test_get_post_empty(client: AsyncClient):
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert data["has_more"] is False
    assert data["posts"] == []


# test if a person as for post which is not present in database
@pytest.mark.anyio
async def test_get_post_by_id(client: AsyncClient, post_id: int = 999):

    response = await client.get("/post/api/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found for 999"


# test for post blog post
@pytest.mark.anyio
async def test_create_post(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.post(
        "/post/api/post",
        json={
            "title": "My first post",
            "description": "This is the first post",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first post"
    assert data["description"] == "This is the first post"
    assert data["user_id"] == user["id"]
    assert "id" in data
