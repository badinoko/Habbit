from __future__ import annotations

import re
from types import SimpleNamespace

import pytest

from src.config import settings
from src.schemas.auth import AuthUser
from tests.helpers import make_auth_user


class _FakeAuthService:
    def __init__(self) -> None:
        self.register_result = make_auth_user("new@example.com")
        self.register_error: Exception | None = None
        self.authenticate_result: AuthUser | None = None
        self.oauth_user_result: AuthUser = make_auth_user("oauth@example.com")
        self.oauth_user_error: Exception | None = None
        self.google_start_error: Exception | None = None
        self.google_callback_error: Exception | None = None
        self.register_calls: list[object] = []
        self.authenticate_calls: list[object] = []
        self.oauth_user_calls: list[dict[str, str]] = []
        self.google_start_calls: list[dict[str, str]] = []
        self.google_callback_calls: list[dict[str, object]] = []
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

    async def get_or_create_oauth_user(
        self,
        *,
        email: str,
        provider: str,
        provider_user_id: str,
    ) -> AuthUser:
        self.oauth_user_calls.append(
            {
                "email": email,
                "provider": provider,
                "provider_user_id": provider_user_id,
            }
        )
        if self.oauth_user_error is not None:
            raise self.oauth_user_error
        return self.oauth_user_result

    async def login_create_session(self, user_id) -> str:  # noqa: ANN001
        self.created_session_for.append(str(user_id))
        return "session-123"

    async def logout(self, session_id: str, user_id) -> None:  # noqa: ANN001
        self.logout_calls.append((session_id, str(user_id)))

    def start_google_oauth_login(self, *, next_url: str) -> SimpleNamespace:
        self.google_start_calls.append({"next_url": next_url})
        if self.google_start_error is not None:
            raise self.google_start_error
        return SimpleNamespace(
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth?state=fake-state",
            session_payload={
                "state": "fake-state",
                "next": next_url,
                "issued_at": "2026-03-08T12:00:00Z",
            },
        )

    async def complete_google_oauth_login(
        self,
        *,
        oauth_session: object,
        provided_state: object,
        provider_error: object,
        code: object,
    ) -> SimpleNamespace:
        self.google_callback_calls.append(
            {
                "oauth_session": oauth_session,
                "provided_state": provided_state,
                "provider_error": provider_error,
                "code": code,
            }
        )
        if self.google_callback_error is not None:
            raise self.google_callback_error

        self.oauth_user_calls.append(
            {
                "email": "oauth@example.com",
                "provider": "google",
                "provider_user_id": "google-user-123",
            }
        )
        self.created_session_for.append(str(self.oauth_user_result.id))
        next_url = "/"
        if isinstance(oauth_session, dict):
            next_url = str(oauth_session.get("next") or "/")
        return SimpleNamespace(
            next_url=next_url,
            session_id="session-123",
            user=self.oauth_user_result,
        )


def _extract_form(html: str, action: str) -> str:
    match = re.search(
        rf'<form[^>]*action="{re.escape(action)}"[^>]*>(.*?)</form>',
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group(1)


def _extract_google_oauth_href(html: str) -> str:
    match = re.search(
        r'<a href="([^"]+)" class="btn auth-oauth-btn">',
        html,
    )
    assert match is not None
    return match.group(1)


@pytest.fixture(autouse=True)
def configure_google_oauth() -> None:
    original_client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    original_client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
    original_redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    settings.GOOGLE_OAUTH_CLIENT_ID = "google-client-id"
    settings.GOOGLE_OAUTH_CLIENT_SECRET = "google-client-secret"
    settings.GOOGLE_OAUTH_REDIRECT_URI = "http://test/auth/google/callback"
    try:
        yield
    finally:
        settings.GOOGLE_OAUTH_CLIENT_ID = original_client_id
        settings.GOOGLE_OAUTH_CLIENT_SECRET = original_client_secret
        settings.GOOGLE_OAUTH_REDIRECT_URI = original_redirect_uri
