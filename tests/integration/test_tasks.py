import itertools
from uuid import UUID, uuid4

import pytest

from src.repositories import TaskRepository, ThemeRepository
from src.schemas import TaskCreateAPI, ThemeCreate
from src.services import TaskService

NAME = "Читать книги"
THEME_NAME = "Хобби"
DESCRIPTION = "30 минут в день"
PRIORITY = "low"


async def mark_task_as_completed(client, id):
    return await client.patch(f"/tasks/{id}/complete")


async def mark_task_as_incompleted(client, id):
    return await client.patch(f"/tasks/{id}/incomplete")


async def delete_task(client, id):
    return await client.delete(f"/tasks/{id}")


async def update_task(client, id, data):
    return await client.put(f"/tasks/{id}/edit", json=data)


@pytest.mark.asyncio
async def test_create_task(client, session):
    # Простой случай
    data = {"name": NAME, "priority": PRIORITY}
    response = await client.post("/tasks/", data=data)
    assert response.status_code == 303  # перенаправление

    # Случай с темой и описанием
    theme_repo = ThemeRepository(session=session)
    theme = await theme_repo.add(ThemeCreate(name=THEME_NAME, color="#FF5733"))
    await session.commit()
    data.update({"description": DESCRIPTION, "theme_id": theme.id})
    response = await client.post("/tasks/", data=data)
    assert response.status_code == 303  # перенаправление


@pytest.mark.asyncio
async def test_create_task_error(client):
    # Отсутсвует название
    data = {"priority": PRIORITY}
    response = await client.post("/tasks/", data=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_mark_task_as_completed(client, session):
    id = await create_task_and_return_id(session)
    res = await mark_task_as_completed(client, id)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_mark_as_completed_task_not_found(client):
    res = await mark_task_as_completed(client, uuid4())
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_mark_task_as_incompleted(client, session):
    id = await create_task_and_return_id(session)
    res = await mark_task_as_completed(client, id)
    assert res.status_code == 200
    res = await mark_task_as_incompleted(client, id)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_mark_as_incompleted_task_not_found(client):
    res = await mark_task_as_incompleted(client, uuid4())
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(client, session):
    id = await create_task_and_return_id(session)
    response = await delete_task(client, id)
    assert response.status_code == 204

    response = await client.get("/tasks/")
    assert response.status_code == 200
    assert NAME not in response.text

    response = await delete_task(client, id)  # Идемпотентность метода delete
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_task(client, session):
    id = await create_task_and_return_id(session)

    def all_subsets_dict(data: dict):
        keys = list(data.keys())
        result = []
        # перебираем длину подмножества
        for r in range(1, len(keys) + 1):
            # все комбинации ключей длины r
            for comb in itertools.combinations(keys, r):
                subset = {
                    k: (str(data[k]) if isinstance(data[k], UUID) else data[k])
                    for k in comb
                }
                result.append(subset)
        return result

    theme_repo = ThemeRepository(session=session)
    theme = await theme_repo.add(ThemeCreate(name=THEME_NAME, color="#FF5733"))
    await session.commit()

    fields_that_can_be_updated = {
        "name": NAME,
        "description": DESCRIPTION,
        "theme_id": theme.id,
        "priority": PRIORITY,
    }
    result = all_subsets_dict(fields_that_can_be_updated)

    for data in result:
        response = await update_task(client, id, data)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_tasks_list_page(client, session):
    await create_task_and_return_id(session)  # название task'а == NAME
    response = await client.get("/tasks/")
    assert response.status_code == 200
    assert NAME in response.text


@pytest.mark.asyncio
async def test_task_creation_page(client, session):
    response = await client.get("/tasks/new")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_task_update_page(client, session):
    id = await create_task_and_return_id(session)
    response = await client.get(f"/tasks/{id}")
    assert response.status_code == 200
    assert NAME in response.text


async def create_task_and_return_id(session):
    task_repo = TaskRepository(session=session)
    theme_repo = ThemeRepository(session=session)

    task_service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    response = await task_service.create_task(
        task_data=TaskCreateAPI(name=NAME, priority=PRIORITY)
    )
    await session.commit()
    id = response.model_dump()["id"]
    return id
