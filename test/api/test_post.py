import pytest
from conftest import async_header, create_test_user, login_test_user
from httpx import AsyncClient

# dummy post json
dummy_post_json = {
    "title": "My first post",
    "description": "This is the first post",
}


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

    response = await client.get(f"/post/api/{post_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found for 999"


# test for blog post
@pytest.mark.anyio
async def test_create_post_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.post(
        "/post/api/post",
        json=dummy_post_json,
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == dummy_post_json["title"]
    assert data["description"] == dummy_post_json["description"]
    assert data["user_id"] == user["id"]
    assert "id" in data


# test if post request was made without authenticating
@pytest.mark.anyio
async def test_post_without_auth(client: AsyncClient):

    response = await client.post(
        "/post/api/post",
        json={"title": "My first post", "description": "This is the first post"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# test for update blog post
@pytest.mark.anyio
async def test_patch_blog_post_success(client: AsyncClient):

    user = await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.post(
        "/post/api/post",
        json=dummy_post_json,
        headers=headers,
    )

    post_id = response.json()["id"]

    response = await client.patch(
        f"/post/api/update/{post_id}",
        json={
            "title": "My first Post part 2",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["user_id"] == user["id"]
    assert data["title"] == "My first Post part 2"
    assert data["description"] == dummy_post_json["description"]


# test update post for not existing post id
@pytest.mark.anyio
async def test_patch_blob_post_id_not_exist(client: AsyncClient, post_id: int = 999):

    await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.patch(
        f"/post/api/update/{post_id}",
        json={
            "title": "My first Post part 2",
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Post not found {post_id}"


# test update post without auth
@pytest.mark.anyio
async def test_patch_blog_post_id_without_auth(client: AsyncClient, post_id: int = 999):

    await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.post(
        "/post/api/post",
        json=dummy_post_json,
        headers=headers,
    )

    post_id = response.json()["id"]

    response = await client.patch(
        f"/post/api/update/{post_id}",
        json={
            "title": "My first Post part 2",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# test for delete blog post success
@pytest.mark.anyio
async def test_delete_blog_post_success(client: AsyncClient):

    await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.post(
        "/post/api/post", json=dummy_post_json, headers=headers
    )

    post_id = response.json()["id"]

    response = await client.delete(f"/post/api/delete/{post_id}", headers=headers)

    assert response.status_code == 204

    check_response = await client.get(f"/post/api/{post_id}")

    assert check_response.status_code == 404


# test for delete blog post for not existing id
@pytest.mark.anyio
async def test_delete_blog_post_id_not_exist(client: AsyncClient, post_id: int = 999):

    await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.delete(f"/post/api/delete/{post_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == f"Post not found {post_id}"


# test for delete blog post without auth
@pytest.mark.anyio
async def test_delete_blog_post_without_auth(client: AsyncClient):

    await create_test_user(client)
    token = await login_test_user(client)
    headers = async_header(token)

    response = await client.post(
        "/post/api/post", json=dummy_post_json, headers=headers
    )

    post_id = response.json()["id"]

    response = await client.delete(f"/post/api/delete/{post_id}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
