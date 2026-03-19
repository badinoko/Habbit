import re

import pytest
from sqlalchemy.exc import IntegrityError

from tests.helpers import with_csrf_form, with_csrf_headers

NAME = "Хобби"
COLOR = "#FF00FF"


async def create_theme(client, name: str | None = None, color: str | None = None):
    data = {}
    if name is not None:
        data["name"] = name
    if color is not None:
        data["color"] = color
    return await client.post(
        "/themes/",
        data=await with_csrf_form(client, data, path="/themes/new"),
    )


async def update_theme(client, id, name=None, color=None):
    data = {}
    if name is not None:
        data["name"] = name
    if color is not None:
        data["color"] = color
    return await client.put(
        f"/themes/{id}",
        json=data,
        headers=await with_csrf_headers(client),
    )


async def delete_theme(client, id):
    return await client.delete(
        f"/themes/{id}",
        headers=await with_csrf_headers(client),
    )


async def get_theme_id_by_name(client, name: str) -> str:
    response = await client.get("/themes/")
    assert response.status_code == 200

    # theme-card содержит атрибуты data-theme-id и data-theme-name
    pattern = (
        r'data-theme-id="(?P<id>[^"]+)"[^>]*data-theme-name="'
        + re.escape(name)
        + r'"'
    )
    match = re.search(pattern, response.text)
    assert match, f"Theme id not found for name={name!r}"
    theme_id = match.group("id").strip()
    # Важно: роуты ожидают валидный UUID, иначе будет 422
    import uuid

    uuid.UUID(theme_id)
    return theme_id


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
async def test_theme_repository_enforces_unique_name_per_owner(session, owner_id):
    from src.repositories import ThemeRepository
    from src.schemas import ThemeCreate

    repo = ThemeRepository(session=session, owner_id=owner_id)
    await repo.add(ThemeCreate(name="Личное", color="#AA11BB"))
    await session.commit()

    with pytest.raises(IntegrityError):
        await repo.add(ThemeCreate(name="Личное", color="#11BBAA"))
        await session.commit()

    await session.rollback()


@pytest.mark.asyncio
async def test_different_owners_can_create_themes_with_same_name(
    session, owner_id, secondary_owner_id
):
    from src.repositories import ThemeRepository
    from src.schemas import ThemeCreate

    primary_repo = ThemeRepository(session=session, owner_id=owner_id)
    secondary_repo = ThemeRepository(session=session, owner_id=secondary_owner_id)

    first = await primary_repo.add(ThemeCreate(name="Общее имя", color="#AA11BB"))
    second = await secondary_repo.add(ThemeCreate(name="Общее имя", color="#11BBAA"))
    await session.commit()

    assert first.name == second.name
    assert first.id != second.id
    assert await primary_repo.get_by_name("Общее имя") == first
    assert await secondary_repo.get_by_name("Общее имя") == second


@pytest.mark.asyncio
async def test_create_theme_without_name_error(client):
    response = await create_theme(client=client, name=None, color=COLOR)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_theme(client):
    await create_theme(client=client, name=NAME)
    theme_id = await get_theme_id_by_name(client, NAME)
    response = await update_theme(
        client=client, id=theme_id, name="Новое название", color="#FFFFFF"
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
    theme_id = await get_theme_id_by_name(client, NAME)
    response = await delete_theme(client=client, id=theme_id)
    assert response.status_code == 204

    response = await client.get("/themes/")
    assert response.status_code == 200
    assert NAME not in response.text


@pytest.mark.asyncio
async def test_get_update_theme_page(client):
    await create_theme(client=client, name=NAME)
    theme_id = await get_theme_id_by_name(client, NAME)
    response = await client.get(f"/themes/{theme_id}")
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


@pytest.mark.asyncio
async def test_theme_owner_scope_hides_foreign_theme_and_blocks_mutations(
    client, secondary_client
):
    foreign_theme_name = "Чужая тема B"

    create_response = await create_theme(client=secondary_client, name=foreign_theme_name)
    assert create_response.status_code == 303
    foreign_theme_id = await get_theme_id_by_name(secondary_client, foreign_theme_name)

    list_response = await client.get("/themes/")
    assert list_response.status_code == 200
    assert foreign_theme_name not in list_response.text

    detail_response = await client.get(f"/themes/{foreign_theme_id}")
    assert detail_response.status_code == 404
    assert "Тема не найдена" in detail_response.text

    update_response = await update_theme(
        client=client,
        id=foreign_theme_id,
        name="Чужое обновление",
    )
    assert update_response.status_code == 404

    delete_response = await delete_theme(client=client, id=foreign_theme_id)
    assert delete_response.status_code == 404

    owner_detail_response = await secondary_client.get(f"/themes/{foreign_theme_id}")
    assert owner_detail_response.status_code == 200
    assert foreign_theme_name in owner_detail_response.text


@pytest.mark.asyncio
async def test_theme_repository_with_missing_owner_is_fail_closed(session, owner_id):
    from src.repositories import ThemeRepository
    from src.schemas import ThemeCreate

    owner_repo = ThemeRepository(session=session, owner_id=owner_id)
    theme = await owner_repo.add(ThemeCreate(name="Owner theme", color="#AABBCC"))
    await session.commit()

    guest_repo = ThemeRepository(session=session, owner_id=None)

    guest_theme = await guest_repo.get_by_id(theme.id)
    guest_by_name = await guest_repo.get_by_name("Owner theme")
    guest_count = await guest_repo.count_themes()
    guest_list_with_counts = await guest_repo.list_with_counts()

    assert guest_theme is None
    assert guest_by_name is None
    assert guest_count == 0
    assert guest_list_with_counts == []
