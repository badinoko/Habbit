from __future__ import annotations

import re
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from src.routers import auth as auth_module
from src.config import settings
from src.dependencies import get_auth_service, get_current_user, _is_html_request
from src.exceptions import EmailAlreadyExistsError
from src.routers.auth import _normalize_next
from src.routers.auth import router as auth_router
from src.schemas.auth import AuthUser

pytestmark = pytest.mark.asyncio


def _mk_user(email: str = "user@example.com") -> AuthUser:
    now = datetime(2026, 3, 8, 12, 0, tzinfo=UTC)
    return AuthUser(
        id=uuid4(),
        email=email,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


class _FakeAuthService:
    def __init__(self) -> None:
        self.register_result = _mk_user("new@example.com")
        self.register_error: Exception | None = None
        self.authenticate_result: AuthUser | None = None
        self.register_calls: list[object] = []
        self.authenticate_calls: list[object] = []
        self.created_session_for: list[str] = []
        self.logout_calls: list[tuple[str, str]] = []

    async def register(self, payload) -> AuthUser:  # noqa: ANN001
        self.register_calls.append(payload)
        if self.register_error is not None:
            raise self.register_error
        return self.register_result

    async def authenticate(self, payload) -> AuthUser | None:  # noqa: ANN001
        self.authenticate_calls.append(payload)
        return self.authenticate_result

    async def login_create_session(self, user_id) -> str:  # noqa: ANN001
        self.created_session_for.append(str(user_id))
        return "session-123"

    async def logout(self, session_id: str, user_id) -> None:  # noqa: ANN001
        self.logout_calls.append((session_id, str(user_id)))


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


@pytest.mark.parametrize(
    ("next_value", "expected"),
    [
        (None, "/"),
        ("", "/"),
        ("/tasks", "/tasks"),
        ("tasks", "/"),
        ("//evil.example", "/"),
        ("https://evil.example/path", "/"),
    ],
)
async def test_normalize_next_rejects_unsafe_targets(
    next_value: str | None,
    expected: str,
) -> None:
    assert _normalize_next(next_value) == expected


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({"accept": "text/html"}, True),
        ({"content-type": "application/x-www-form-urlencoded"}, True),
        ({"content-type": "multipart/form-data; boundary=abc"}, True),
        ({"accept": "application/json", "content-type": "application/json"}, False),
    ],
)
async def test_is_html_request_detects_browser_requests(
    headers: dict[str, str],
    expected: bool,
) -> None:
    app = FastAPI()

    @app.get("/probe")
    async def probe(request: Request) -> dict[str, bool]:
        return {"is_html": _is_html_request(request)}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        res = await http_client.get("/probe", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"is_html": expected}


@pytest.fixture
async def client() -> AsyncGenerator[
    tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
    None,
]:
    app = FastAPI()
    fake_auth_service = _FakeAuthService()
    current_user_state = {"value": None}

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        session_cookie=settings.UI_SESSION_COOKIE_NAME,
    )
    app.mount("/static", StaticFiles(directory="src/static"), name="static")
    app.include_router(auth_router)

    async def override_current_user():
        return current_user_state["value"]

    app.dependency_overrides[get_auth_service] = lambda: fake_auth_service
    app.dependency_overrides[get_current_user] = override_current_user
    app.state.current_user_state = current_user_state

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            yield http_client, fake_auth_service, current_user_state
    finally:
        app.dependency_overrides.clear()


async def test_login_page_renders_csrf_and_normalizes_unsafe_next(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.get(
        "/auth/login?next=https://evil.example",
        headers={"Accept": "text/html"},
    )

    assert res.status_code == 200
    assert 'name="csrf_token"' in res.text
    assert 'name="next" value="/"' in res.text


async def test_login_page_redirects_authenticated_user_to_safe_next(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, current_user_state = client
    current_user_state["value"] = _mk_user()

    res = await http_client.get(
        "/auth/login?next=https://evil.example",
        headers={"Accept": "text/html"},
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/"


async def test_register_page_redirects_authenticated_user(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, current_user_state = client
    current_user_state["value"] = _mk_user()

    res = await http_client.get(
        "/auth/register?next=/tasks",
        headers={"Accept": "text/html"},
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/tasks"


async def test_login_form_rejects_missing_csrf_token(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/login",
        headers={"Accept": "text/html"},
        data={"email": "user@example.com", "password": "strong-pass-123", "next": "/tasks"},
    )

    assert res.status_code == 403
    assert res.headers["content-type"].startswith("text/html")
    assert "Сессия формы истекла или стала недействительной." in res.text
    assert 'name="csrf_token"' in res.text


async def test_login_form_rejects_invalid_csrf_token(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    page = await http_client.get("/auth/login", headers={"Accept": "text/html"})
    assert _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/login",
        headers={"Accept": "text/html"},
        data={
            "email": "user@example.com",
            "password": "strong-pass-123",
            "csrf_token": "invalid-token",
            "next": "/tasks",
        },
    )

    assert res.status_code == 403
    assert res.headers["content-type"].startswith("text/html")
    assert "Сессия формы истекла или стала недействительной." in res.text
    assert 'value="user@example.com"' in res.text


async def test_register_form_rejects_invalid_csrf_token_with_html_error(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    page = await http_client.get("/auth/register", headers={"Accept": "text/html"})
    assert _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/register",
        headers={"Accept": "text/html"},
        data={
            "email": "new@example.com",
            "password": "strong-pass-123",
            "csrf_token": "invalid-token",
            "next": "/tasks",
        },
    )

    assert res.status_code == 403
    assert res.headers["content-type"].startswith("text/html")
    assert "Сессия формы истекла или стала недействительной." in res.text
    assert 'value="new@example.com"' in res.text


async def test_login_form_redirects_after_success(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.authenticate_result = _mk_user()

    page = await http_client.get("/auth/login?next=/tasks", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/login",
        headers={"Accept": "text/html"},
        data={
            "email": "user@example.com",
            "password": "strong-pass-123",
            "csrf_token": csrf_token,
            "next": "/tasks",
        },
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/tasks"
    assert settings.AUTH_SESSION_COOKIE_NAME in res.headers.get("set-cookie", "")


async def test_login_json_returns_user_and_sets_cookie(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.authenticate_result = _mk_user()

    res = await http_client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["email"] == "user@example.com"
    assert settings.AUTH_SESSION_COOKIE_NAME in res.headers.get("set-cookie", "")


async def test_login_json_returns_409_for_authenticated_user_without_auth_attempt(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, current_user_state = client
    current_user_state["value"] = _mk_user()

    res = await http_client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )

    assert res.status_code == 409
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Already authenticated"
    assert fake_auth_service.authenticate_calls == []
    assert fake_auth_service.created_session_for == []


@pytest.mark.parametrize(
    ("path", "payload", "prepare_service"),
    [
        (
            "/auth/login",
            {"email": "user@example.com", "password": "strong-pass-123"},
            lambda service: setattr(service, "authenticate_result", _mk_user()),
        ),
        (
            "/auth/register",
            {"email": "new@example.com", "password": "strong-pass-123"},
            lambda service: setattr(service, "register_result", _mk_user("new@example.com")),
        ),
    ],
)
async def test_json_auth_endpoints_do_not_render_html_templates(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    payload: dict[str, str],
    prepare_service,
) -> None:
    http_client, fake_auth_service, _state = client
    prepare_service(fake_auth_service)

    def fail_on_render(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("HTML template render should not happen for JSON requests")

    monkeypatch.setattr(auth_module, "_render_auth_template", fail_on_render)

    res = await http_client.post(path, json=payload)

    assert res.status_code in {200, 201}
    assert res.headers["content-type"].startswith("application/json")


async def test_login_json_rejects_invalid_credentials(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.authenticate_result = None

    res = await http_client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )

    assert res.status_code == 401
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Invalid email or password"


async def test_login_json_rejects_invalid_payload_with_422(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "short"},
    )

    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_login_json_rejects_malformed_json_body(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/login",
        content="{",
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 400
    assert res.json()["detail"] == "Malformed JSON body"


async def test_login_rejects_unsupported_media_type_with_415(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/login",
        content="email=user@example.com",
        headers={"Content-Type": "text/plain"},
    )

    assert res.status_code == 415
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Unsupported Media Type"


async def test_login_form_returns_generic_error_on_invalid_credentials(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.authenticate_result = None

    page = await http_client.get("/auth/login", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/login",
        headers={"Accept": "text/html"},
        data={
            "email": "user@example.com",
            "password": "wrong-password",
            "csrf_token": csrf_token,
            "next": "/",
        },
    )

    assert res.status_code == 401
    assert "Неверный email или пароль." in res.text
    assert "wrong-password" not in res.text


async def test_login_form_returns_validation_error_for_invalid_payload(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    page = await http_client.get("/auth/login", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/login",
        headers={"Accept": "text/html"},
        data={
            "email": "not-an-email",
            "password": "strong-pass-123",
            "csrf_token": csrf_token,
            "next": "/tasks",
        },
    )

    assert res.status_code == 400
    assert "Укажите корректный email и пароль." in res.text
    assert 'value="not-an-email"' in res.text


async def test_register_form_returns_validation_error_and_preserves_email(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    page = await http_client.get("/auth/register", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/register",
        headers={"Accept": "text/html"},
        data={
            "email": "new@example.com",
            "password": "short",
            "csrf_token": csrf_token,
            "next": "/tasks",
        },
    )

    assert res.status_code == 400
    assert "Проверьте email и пароль" in res.text
    assert 'value="new@example.com"' in res.text


async def test_register_form_redirects_after_success(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.register_result = _mk_user("new@example.com")

    page = await http_client.get("/auth/register?next=/tasks", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/register",
        headers={"Accept": "text/html"},
        data={
            "email": "new@example.com",
            "password": "strong-pass-123",
            "csrf_token": csrf_token,
            "next": "/tasks",
        },
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/tasks"
    assert settings.AUTH_SESSION_COOKIE_NAME in res.headers.get("set-cookie", "")


async def test_register_form_returns_conflict_error_when_email_exists(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.register_error = EmailAlreadyExistsError()

    page = await http_client.get("/auth/register", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    res = await http_client.post(
        "/auth/register",
        headers={"Accept": "text/html"},
        data={
            "email": "new@example.com",
            "password": "strong-pass-123",
            "csrf_token": csrf_token,
            "next": "/tasks",
        },
    )

    assert res.status_code == 409
    assert "Пользователь с таким email уже существует." in res.text


async def test_register_json_returns_user_and_sets_cookie(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.register_result = _mk_user("new@example.com")

    res = await http_client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "strong-pass-123"},
    )

    assert res.status_code == 201
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["email"] == "new@example.com"
    assert settings.AUTH_SESSION_COOKIE_NAME in res.headers.get("set-cookie", "")


async def test_register_json_returns_409_for_authenticated_user_without_register_attempt(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, current_user_state = client
    current_user_state["value"] = _mk_user()

    res = await http_client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "strong-pass-123"},
    )

    assert res.status_code == 409
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Already authenticated"
    assert fake_auth_service.register_calls == []
    assert fake_auth_service.created_session_for == []


async def test_register_json_rejects_invalid_payload_with_422(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/register",
        json={"email": "bad-email", "password": "short"},
    )

    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_register_json_returns_conflict_when_email_exists(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client
    fake_auth_service.register_error = EmailAlreadyExistsError()

    res = await http_client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "strong-pass-123"},
    )

    assert res.status_code == 409
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Email already exists"


async def test_register_json_rejects_malformed_json_body(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/register",
        content="{",
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 400
    assert res.json()["detail"] == "Malformed JSON body"


async def test_register_json_rejects_non_object_json_body(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/register",
        content='["not", "an", "object"]',
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 400
    assert res.json()["detail"] == "JSON body must be an object"


async def test_register_rejects_unsupported_media_type_with_415(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, _, _state = client

    res = await http_client.post(
        "/auth/register",
        content="<email>new@example.com</email>",
        headers={"Content-Type": "application/xml"},
    )

    assert res.status_code == 415
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Unsupported Media Type"


async def test_logout_form_clears_cookie_and_redirects_home(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, current_user_state = client
    page = await http_client.get("/auth/login", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    current_user = _mk_user()
    http_client.cookies.set(settings.AUTH_SESSION_COOKIE_NAME, "session-123")
    current_user_state["value"] = current_user

    res = await http_client.post(
        "/auth/logout",
        headers={"Accept": "text/html"},
        data={"csrf_token": csrf_token, "next": "/"},
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/"
    assert fake_auth_service.logout_calls == [("session-123", str(current_user.id))]
    assert f"{settings.AUTH_SESSION_COOKIE_NAME}=" in res.headers.get("set-cookie", "")


async def test_logout_form_normalizes_unsafe_next_target(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, current_user_state = client
    page = await http_client.get("/auth/login", headers={"Accept": "text/html"})
    csrf_token = _extract_csrf_token(page.text)

    current_user = _mk_user()
    http_client.cookies.set(settings.AUTH_SESSION_COOKIE_NAME, "session-unsafe")
    current_user_state["value"] = current_user

    res = await http_client.post(
        "/auth/logout",
        headers={"Accept": "text/html"},
        data={"csrf_token": csrf_token, "next": "https://evil.example"},
        follow_redirects=False,
    )

    assert res.status_code == 303
    assert res.headers["location"] == "/"
    assert fake_auth_service.logout_calls == [("session-unsafe", str(current_user.id))]


async def test_logout_form_rejects_invalid_csrf_token_with_html_error(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, current_user_state = client
    page = await http_client.get("/auth/login", headers={"Accept": "text/html"})
    assert _extract_csrf_token(page.text)

    current_user_state["value"] = _mk_user()

    res = await http_client.post(
        "/auth/logout",
        headers={"Accept": "text/html"},
        data={"csrf_token": "invalid-token", "next": "/"},
    )

    assert res.status_code == 403
    assert res.headers["content-type"].startswith("text/html")
    assert "Не удалось выполнить выход" in res.text
    assert "Сессия формы истекла или стала недействительной." in res.text
    assert fake_auth_service.logout_calls == []


async def test_logout_json_logs_out_and_clears_cookie(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, current_user_state = client
    current_user = _mk_user()
    current_user_state["value"] = current_user
    http_client.cookies.set(settings.AUTH_SESSION_COOKIE_NAME, "session-json")

    res = await http_client.post("/auth/logout", json={"next": "/tasks"})

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {"message": "Logged out"}
    assert fake_auth_service.logout_calls == [("session-json", str(current_user.id))]
    assert f"{settings.AUTH_SESSION_COOKIE_NAME}=" in res.headers.get("set-cookie", "")


async def test_logout_json_without_user_or_session_skips_service_call(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client

    res = await http_client.post("/auth/logout", json={})

    assert res.status_code == 200
    assert res.json() == {"message": "Logged out"}
    assert fake_auth_service.logout_calls == []


async def test_logout_rejects_unsupported_media_type_with_415(
    client: tuple[AsyncClient, _FakeAuthService, dict[str, AuthUser | None]],
) -> None:
    http_client, fake_auth_service, _state = client

    res = await http_client.post(
        "/auth/logout",
        content="next=/tasks",
        headers={"Content-Type": "text/plain"},
    )

    assert res.status_code == 415
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Unsupported Media Type"
    assert fake_auth_service.logout_calls == []
