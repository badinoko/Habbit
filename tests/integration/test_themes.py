import pytest

NAME = "Хобби"
COLOR = "#FF00FF"


async def create_theme(client, name: str | None = None, color: str | None = None):
    data = {}
    if name is not None:
        data["name"] = name
    if color is not None:
        data["color"] = color
    return await client.post("/themes/", data=data)


async def update_theme(client, id, name=None, color=None):
    data = {}
    if name is not None:
        data["name"] = name
    if color is not None:
        data["color"] = color
    return await client.put(f"/themes/{id}", json=data)


async def delete_theme(client, id):
    return await client.delete(f"/themes/{id}")


@pytest.mark.asyncio
async def test_create_theme(client):
    # Простой случай
    response = await create_theme(client=client, name=NAME)
    assert response.status_code == 303  # перенаправление

    # Случай с цветом
    response = await create_theme(client=client, name="Работа", color=COLOR)
    assert response.status_code == 303  # Перенаправление


@pytest.mark.asyncio
async def test_create_theme_twice_with_same_name_error(client):
    response = await create_theme(client=client, name=NAME)
    assert response.status_code == 303  # Перенаправление

    response = await create_theme(client=client, name=NAME)
    assert response.status_code == 400  # Ошибка - название темы уже существует


@pytest.mark.asyncio
async def test_create_theme_without_name_error(client):
    response = await create_theme(client=client, name=None, color=COLOR)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_theme(client):
    await create_theme(client=client, name=NAME)
    response = await update_theme(
        client=client, id=NAME, name="Новое название", color="#FFFFFF"
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["status"] == "success"
    assert data["theme"]["name"] == "Новое название"
    assert data["theme"]["color"] == "#FFFFFF"

    response = await client.get("/themes/")
    assert response.status_code == 200
    assert "Новое название" in response.text
    assert NAME not in response.text


@pytest.mark.asyncio
async def test_get_themes_list_page(client):
    await create_theme(client=client, name=NAME)
    response = await client.get("/themes/")
    assert response.status_code == 200
    assert NAME in response.text


@pytest.mark.asyncio
async def test_delete_theme(client):
    await create_theme(client=client, name=NAME)
    response = await delete_theme(client=client, id=NAME)
    assert response.status_code == 204

    response = await client.get("/themes/")
    assert response.status_code == 200
    assert NAME not in response.text


@pytest.mark.asyncio
async def test_get_update_theme_page(client):
    await create_theme(client=client, name=NAME)
    response = await client.get(f"/themes/{NAME}")
    assert response.status_code == 200
    assert NAME in response.text


@pytest.mark.asyncio
async def test_themes_page_redirects_to_first_page_when_empty(client):
    response = await client.get("/themes/?page=3&per_page=5", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/themes/?per_page=5"


@pytest.mark.asyncio
async def test_themes_page_redirects_to_last_page_when_page_is_too_high(client):
    await create_theme(client=client, name="Темы-1")
    await create_theme(client=client, name="Темы-2")
    await create_theme(client=client, name="Темы-3")

    response = await client.get("/themes/?page=9&per_page=2", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/themes/?page=2&per_page=2"
