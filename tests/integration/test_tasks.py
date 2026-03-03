import itertools
from uuid import UUID, uuid4

import pytest

from src.repositories import TaskRepository, ThemeRepository
from src.schemas import TaskCreateAPI, ThemeCreate
from src.services import TaskService
from src.services.tasks import PRIORITY_IDS

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
    return await client.put(f"/tasks/{id}", json=data)


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
    assert res.headers["content-type"].startswith("application/json")
    data = res.json()
    assert data["success"] is True
    assert data["completed"] is True
    assert data["task"]["id"] == str(id)

    task = await TaskRepository(session=session).get_by_id(id)
    assert task is not None
    assert task.completed_at is not None


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
    assert res.headers["content-type"].startswith("application/json")
    data = res.json()
    assert data["success"] is True
    assert data["completed"] is False
    assert data["task"]["id"] == str(id)

    task = await TaskRepository(session=session).get_by_id(id)
    assert task is not None
    assert task.completed_at is None


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
async def test_update_task_persists_payload(client, session):
    task_id = await create_task_and_return_id(session)

    theme_repo = ThemeRepository(session=session)
    theme = await theme_repo.add(ThemeCreate(name="Обновлённая тема", color="#123ABC"))
    await session.commit()

    payload = {
        "name": "Новое имя",
        "description": "Новое описание",
        "priority": "high",
        "theme_id": str(theme.id),
    }
    response = await update_task(client, task_id, payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"message": "success"}

    task = await TaskRepository(session=session).get_by_id(task_id)
    assert task is not None
    assert task.name == "Новое имя"
    assert task.description == "Новое описание"
    assert task.priority_id == PRIORITY_IDS["high"]
    assert task.theme_id == theme.id


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


@pytest.mark.asyncio
async def test_task_update_page_returns_404_when_task_missing(client):
    response = await client.get(f"/tasks/{uuid4()}")
    assert response.status_code == 404
    assert "Задача не найдена" in response.text


@pytest.mark.asyncio
async def test_tasks_list_status_filter_active_and_completed(client, session):
    active_id = await create_task_and_return_id(session, name="status-active")
    completed_id = await create_task_and_return_id(session, name="status-completed")
    await mark_task_as_completed(client, completed_id)

    response = await client.get("/tasks/?status=active")
    assert response.status_code == 200
    assert "status-active" in response.text
    assert "status-completed" not in response.text

    response = await client.get("/tasks/?status=completed")
    assert response.status_code == 200
    assert "status-active" not in response.text
    assert "status-completed" in response.text

    # Санити-чек: задача действительно стала completed в БД.
    completed_task = await TaskRepository(session=session).get_by_id(completed_id)
    assert completed_task is not None
    assert completed_task.completed_at is not None

    active_task = await TaskRepository(session=session).get_by_id(active_id)
    assert active_task is not None
    assert active_task.completed_at is None


@pytest.mark.asyncio
async def test_tasks_list_sort_by_name_and_order(client, session):
    await create_task_and_return_id(session, name="sort-C")
    await create_task_and_return_id(session, name="sort-A")
    await create_task_and_return_id(session, name="sort-B")

    asc_response = await client.get("/tasks/?status=all&sort=name&order=asc")
    assert asc_response.status_code == 200
    asc_text = asc_response.text
    assert (
        asc_text.index("sort-A") < asc_text.index("sort-B") < asc_text.index("sort-C")
    )

    desc_response = await client.get("/tasks/?status=all&sort=name&order=desc")
    assert desc_response.status_code == 200
    desc_text = desc_response.text
    assert (
        desc_text.index("sort-C")
        < desc_text.index("sort-B")
        < desc_text.index("sort-A")
    )


@pytest.mark.asyncio
async def test_tasks_list_pagination(client, session):
    await create_task_and_return_id(session, name="page-A")
    await create_task_and_return_id(session, name="page-B")
    await create_task_and_return_id(session, name="page-C")

    page_1 = await client.get(
        "/tasks/?status=all&sort=name&order=asc&per_page=1&page=1"
    )
    assert page_1.status_code == 200
    assert "page-A" in page_1.text
    assert "page-B" not in page_1.text
    assert "page-C" not in page_1.text

    page_2 = await client.get(
        "/tasks/?status=all&sort=name&order=asc&per_page=1&page=2"
    )
    assert page_2.status_code == 200
    assert "page-A" not in page_2.text
    assert "page-B" in page_2.text
    assert "page-C" not in page_2.text


@pytest.mark.asyncio
async def test_tasks_list_theme_filter_is_persisted_in_session(client, session):
    theme_repo = ThemeRepository(session=session)
    hobby = await theme_repo.add(ThemeCreate(name="Фильтр Хобби", color="#112233"))
    work = await theme_repo.add(ThemeCreate(name="Фильтр Работа", color="#445566"))
    await session.commit()

    await create_task_and_return_id(session, name="task-hobby", theme_id=hobby.id)
    await create_task_and_return_id(session, name="task-work", theme_id=work.id)

    # Выбираем тему через query-параметр -> фильтр сохраняется в session.
    filtered = await client.get("/tasks/?theme=Фильтр Хобби&status=all")
    assert filtered.status_code == 200
    assert "task-hobby" in filtered.text
    assert "task-work" not in filtered.text

    # Без query-параметра фильтр должен остаться активным.
    persisted = await client.get("/tasks/?status=all")
    assert persisted.status_code == 200
    assert "task-hobby" in persisted.text
    assert "task-work" not in persisted.text

    # Сбрасываем фильтр и убеждаемся, что снова видны обе задачи.
    reset = await client.get("/tasks/?theme=Все+темы&status=all")
    assert reset.status_code == 200
    assert "task-hobby" in reset.text
    assert "task-work" in reset.text


async def create_task_and_return_id(
    session,
    *,
    name: str = NAME,
    description: str | None = None,
    theme_id: UUID | None = None,
    priority: str = PRIORITY,
):
    task_repo = TaskRepository(session=session)
    theme_repo = ThemeRepository(session=session)

    task_service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    response = await task_service.create_task(
        task_data=TaskCreateAPI(
            name=name,
            description=description,
            theme_id=theme_id,
            priority=priority,
        )
    )
    await session.commit()
    id = response.model_dump()["id"]
    return id
