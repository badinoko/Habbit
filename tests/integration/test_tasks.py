import itertools
from uuid import UUID, uuid4

import pytest

from src.repositories import TaskRepository, ThemeRepository
from src.schemas import TaskCreateAPI, ThemeCreate
from src.services import TaskService
from src.services.tasks import PRIORITY_IDS
from tests.helpers import with_csrf_form, with_csrf_headers

NAME = "Читать книги"
THEME_NAME = "Хобби"
DESCRIPTION = "30 минут в день"
PRIORITY = "low"
PARTIAL_UPDATE_FIELD_NAMES = ("name", "description", "theme_id", "priority")


async def mark_task_as_completed(client, id):
    return await client.patch(
        f"/tasks/{id}/complete",
        headers=await with_csrf_headers(client),
    )


async def mark_task_as_incompleted(client, id):
    return await client.patch(
        f"/tasks/{id}/incomplete",
        headers=await with_csrf_headers(client),
    )


async def delete_task(client, id):
    return await client.delete(
        f"/tasks/{id}",
        headers=await with_csrf_headers(client),
    )


async def update_task(client, id, data):
    return await client.put(
        f"/tasks/{id}",
        json=data,
        headers=await with_csrf_headers(client),
    )


def _build_partial_update_payloads() -> list[object]:
    updates = {
        "name": "Новое имя (partial)",
        "description": "Новое описание (partial)",
        "theme_id": "UPDATED_THEME_ID",
        "priority": "high",
    }

    payloads = []
    for size in range(1, len(PARTIAL_UPDATE_FIELD_NAMES)):
        for fields in itertools.combinations(PARTIAL_UPDATE_FIELD_NAMES, size):
            payload = {field: updates[field] for field in fields}
            payloads.append(
                pytest.param(payload, id=f"update_{'_'.join(fields)}"),
            )
    return payloads


@pytest.mark.asyncio
async def test_create_task(client, session, owner_id):
    # Простой случай
    data = await with_csrf_form(client, {"name": NAME, "priority": PRIORITY}, path="/tasks/new")
    response = await client.post("/tasks/", data=data)
    assert response.status_code == 303  # перенаправление

    # Случай с темой и описанием
    theme_repo = ThemeRepository(session=session, owner_id=owner_id)
    theme = await theme_repo.add(ThemeCreate(name=THEME_NAME, color="#FF5733"))
    await session.commit()
    data = await with_csrf_form(
        client,
        {
            "name": NAME,
            "priority": PRIORITY,
            "description": DESCRIPTION,
            "theme_id": theme.id,
        },
        path="/tasks/new",
    )
    response = await client.post("/tasks/", data=data)
    assert response.status_code == 303  # перенаправление


@pytest.mark.asyncio
async def test_create_task_error(client):
    # Отсутсвует название
    data = {"priority": PRIORITY}
    response = await client.post("/tasks/", data=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_mark_task_as_completed(client, session, owner_id):
    id = await create_task_and_return_id(session, owner_id=owner_id)
    res = await mark_task_as_completed(client, id)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    data = res.json()
    assert data["success"] is True
    assert data["completed"] is True
    assert data["task"]["id"] == str(id)

    task = await TaskRepository(session=session, owner_id=owner_id).get_by_id(id)
    assert task is not None
    assert task.completed_at is not None


@pytest.mark.asyncio
async def test_mark_as_completed_task_not_found(client):
    res = await mark_task_as_completed(client, uuid4())
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_mark_task_as_incompleted(client, session, owner_id):
    id = await create_task_and_return_id(session, owner_id=owner_id)
    res = await mark_task_as_completed(client, id)
    assert res.status_code == 200
    res = await mark_task_as_incompleted(client, id)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    data = res.json()
    assert data["success"] is True
    assert data["completed"] is False
    assert data["task"]["id"] == str(id)

    task = await TaskRepository(session=session, owner_id=owner_id).get_by_id(id)
    assert task is not None
    assert task.completed_at is None


@pytest.mark.asyncio
async def test_mark_as_incompleted_task_not_found(client):
    res = await mark_task_as_incompleted(client, uuid4())
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(client, session, owner_id):
    id = await create_task_and_return_id(session, owner_id=owner_id)
    response = await delete_task(client, id)
    assert response.status_code == 204

    response = await client.get("/tasks/")
    assert response.status_code == 200
    assert NAME not in response.text

    response = await delete_task(client, id)
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", _build_partial_update_payloads())
async def test_update_task_partial_updates_persist_changed_and_keep_unchanged_fields(
    client, session, owner_id, payload
):
    theme_repo = ThemeRepository(session=session, owner_id=owner_id)
    initial_theme = await theme_repo.add(
        ThemeCreate(name="Начальная тема partial", color="#FF5733")
    )
    updated_theme = await theme_repo.add(
        ThemeCreate(name="Новая тема partial", color="#123ABC")
    )
    await session.commit()

    initial_name = "Исходное имя"
    initial_description = "Исходное описание"
    initial_priority = "medium"

    task_id = await create_task_and_return_id(
        session,
        owner_id=owner_id,
        name=initial_name,
        description=initial_description,
        theme_id=initial_theme.id,
        priority=initial_priority,
    )

    request_payload = dict(payload)
    if "theme_id" in request_payload:
        request_payload["theme_id"] = str(updated_theme.id)

    response = await update_task(client, task_id, request_payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"message": "success"}

    task = await TaskRepository(session=session, owner_id=owner_id).get_by_id(task_id)
    assert task is not None

    assert task.name == (
        "Новое имя (partial)" if "name" in request_payload else initial_name
    )
    assert task.description == (
        "Новое описание (partial)"
        if "description" in request_payload
        else initial_description
    )
    assert task.theme_id == (
        updated_theme.id if "theme_id" in request_payload else initial_theme.id
    )
    assert task.priority_id == (
        PRIORITY_IDS["high"]
        if "priority" in request_payload
        else PRIORITY_IDS[initial_priority]
    )


@pytest.mark.asyncio
async def test_update_task_persists_payload(client, session, owner_id):
    task_id = await create_task_and_return_id(session, owner_id=owner_id)

    theme_repo = ThemeRepository(session=session, owner_id=owner_id)
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

    task = await TaskRepository(session=session, owner_id=owner_id).get_by_id(task_id)
    assert task is not None
    assert task.name == "Новое имя"
    assert task.description == "Новое описание"
    assert task.priority_id == PRIORITY_IDS["high"]
    assert task.theme_id == theme.id


@pytest.mark.asyncio
async def test_tasks_list_page(client, session, owner_id):
    await create_task_and_return_id(session, owner_id=owner_id)  # название task'а == NAME
    response = await client.get("/tasks/")
    assert response.status_code == 200
    assert NAME in response.text


@pytest.mark.asyncio
async def test_task_creation_page(client, session):
    response = await client.get("/tasks/new")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_task_update_page(client, session, owner_id):
    id = await create_task_and_return_id(session, owner_id=owner_id)
    response = await client.get(f"/tasks/{id}")
    assert response.status_code == 200
    assert NAME in response.text


@pytest.mark.asyncio
async def test_task_update_page_returns_404_when_task_missing(client):
    response = await client.get(f"/tasks/{uuid4()}")
    assert response.status_code == 404
    assert "Задача не найдена" in response.text


@pytest.mark.asyncio
async def test_tasks_list_status_filter_active_and_completed(client, session, owner_id):
    active_id = await create_task_and_return_id(
        session, owner_id=owner_id, name="status-active"
    )
    completed_id = await create_task_and_return_id(
        session, owner_id=owner_id, name="status-completed"
    )
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
    completed_task = await TaskRepository(
        session=session, owner_id=owner_id
    ).get_by_id(completed_id)
    assert completed_task is not None
    assert completed_task.completed_at is not None

    active_task = await TaskRepository(session=session, owner_id=owner_id).get_by_id(
        active_id
    )
    assert active_task is not None
    assert active_task.completed_at is None


@pytest.mark.asyncio
async def test_tasks_list_sort_by_name_and_order(client, session, owner_id):
    await create_task_and_return_id(session, owner_id=owner_id, name="sort-C")
    await create_task_and_return_id(session, owner_id=owner_id, name="sort-A")
    await create_task_and_return_id(session, owner_id=owner_id, name="sort-B")

    asc_response = await client.get("/tasks/?status=active&sort=name&order=asc")
    assert asc_response.status_code == 200
    asc_text = asc_response.text
    assert (
        asc_text.index("sort-A") < asc_text.index("sort-B") < asc_text.index("sort-C")
    )

    desc_response = await client.get("/tasks/?status=active&sort=name&order=desc")
    assert desc_response.status_code == 200
    desc_text = desc_response.text
    assert (
        desc_text.index("sort-C")
        < desc_text.index("sort-B")
        < desc_text.index("sort-A")
    )


@pytest.mark.asyncio
async def test_tasks_list_pagination(client, session, owner_id):
    await create_task_and_return_id(session, owner_id=owner_id, name="page-A")
    await create_task_and_return_id(session, owner_id=owner_id, name="page-B")
    await create_task_and_return_id(session, owner_id=owner_id, name="page-C")

    page_1 = await client.get(
        "/tasks/?status=active&sort=name&order=asc&per_page=1&page=1"
    )
    assert page_1.status_code == 200
    assert "page-A" in page_1.text
    assert "page-B" not in page_1.text
    assert "page-C" not in page_1.text

    page_2 = await client.get(
        "/tasks/?status=active&sort=name&order=asc&per_page=1&page=2"
    )
    assert page_2.status_code == 200
    assert "page-A" not in page_2.text
    assert "page-B" in page_2.text
    assert "page-C" not in page_2.text


@pytest.mark.asyncio
async def test_tasks_list_theme_filter_is_persisted_in_session(client, session, owner_id):
    theme_repo = ThemeRepository(session=session, owner_id=owner_id)
    hobby = await theme_repo.add(ThemeCreate(name="Фильтр Хобби", color="#112233"))
    work = await theme_repo.add(ThemeCreate(name="Фильтр Работа", color="#445566"))
    await session.commit()

    await create_task_and_return_id(
        session, owner_id=owner_id, name="task-hobby", theme_id=hobby.id
    )
    await create_task_and_return_id(
        session, owner_id=owner_id, name="task-work", theme_id=work.id
    )

    # Выбираем тему через query-параметр -> фильтр сохраняется в session.
    filtered = await client.get("/tasks/?theme=Фильтр Хобби&status=active")
    assert filtered.status_code == 200
    assert "task-hobby" in filtered.text
    assert "task-work" not in filtered.text

    # Без query-параметра фильтр должен остаться активным.
    persisted = await client.get("/tasks/?status=active")
    assert persisted.status_code == 200
    assert "task-hobby" in persisted.text
    assert "task-work" not in persisted.text

    # Сбрасываем фильтр и убеждаемся, что снова видны обе задачи.
    reset = await client.get("/tasks/?theme=Все+темы&status=active")
    assert reset.status_code == 200
    assert "task-hobby" in reset.text
    assert "task-work" in reset.text


@pytest.mark.asyncio
async def test_task_owner_scope_hides_foreign_task_and_blocks_mutations(
    client, secondary_client, session, secondary_owner_id
):
    foreign_task_name = "foreign-task-owned-by-user-b"
    foreign_task_id = await create_task_and_return_id(
        session,
        owner_id=secondary_owner_id,
        name=foreign_task_name,
    )

    list_response = await client.get("/tasks/")
    assert list_response.status_code == 200
    assert foreign_task_name not in list_response.text

    detail_response = await client.get(f"/tasks/{foreign_task_id}")
    assert detail_response.status_code == 404
    assert "Задача не найдена" in detail_response.text

    update_response = await update_task(
        client,
        foreign_task_id,
        {"name": "task-overwritten-by-user-a"},
    )
    assert update_response.status_code == 404
    assert update_response.json()["error"]["code"] == "not_found"

    complete_response = await mark_task_as_completed(client, foreign_task_id)
    assert complete_response.status_code == 404

    delete_response = await delete_task(client, foreign_task_id)
    assert delete_response.status_code == 404

    owner_detail_response = await secondary_client.get(f"/tasks/{foreign_task_id}")
    assert owner_detail_response.status_code == 200
    assert foreign_task_name in owner_detail_response.text

    foreign_task = await TaskRepository(
        session=session,
        owner_id=secondary_owner_id,
    ).get_by_id(foreign_task_id)
    assert foreign_task is not None
    assert foreign_task.name == foreign_task_name
    assert foreign_task.completed_at is None


@pytest.mark.asyncio
async def test_task_repository_with_missing_owner_is_fail_closed(session, owner_id):
    task_id = await create_task_and_return_id(session, owner_id=owner_id, name="visible-only-for-owner")

    guest_repo = TaskRepository(session=session, owner_id=None)

    task = await guest_repo.get_by_id(task_id)
    tasks, total = await guest_repo.list_tasks(
        skip=0,
        limit=20,
        theme_id=None,
        status="active",
        sort="created_at",
        order="desc",
    )
    recent = await guest_repo.get_recent_for_dashboard(
        theme_name=None,
        completed=False,
        limit=5,
    )

    assert task is None
    assert tasks == []
    assert total == 0
    assert recent == []


async def create_task_and_return_id(
    session,
    *,
    owner_id: UUID,
    name: str = NAME,
    description: str | None = None,
    theme_id: UUID | None = None,
    priority: str = PRIORITY,
):
    task_repo = TaskRepository(session=session, owner_id=owner_id)
    theme_repo = ThemeRepository(session=session, owner_id=owner_id)

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
