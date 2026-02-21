import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


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
