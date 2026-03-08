from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from argon2.exceptions import InvalidHashError
from sqlalchemy.exc import IntegrityError

from src.exceptions import (
    EmailAlreadyExistsError,
    OAuthIdentityAlreadyLinkedToAnotherUserError,
    ProviderAccountAlreadyLinkedError,
)
from src.schemas.auth import AuthLogin, AuthRegister, AuthUser
from src.services.auth import AuthService


class DummySessionStore:
    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, object]] = {}
        self.user_sessions: dict[str, set[str]] = {}
        self.deleted_sessions: list[str] = []
        self.deleted_user_sessions: list[str] = []

    async def create_session(
        self,
        *,
        session_id: str,
        user_id,
        payload: dict[str, object] | None = None,  # noqa: ANN001
        ttl_seconds: int | None = None,  # noqa: ARG002
    ) -> None:
        normalized_user_id = str(user_id)
        session_payload = dict(payload or {})
        session_payload["user_id"] = normalized_user_id
        self.sessions[session_id] = session_payload
        self.user_sessions.setdefault(normalized_user_id, set()).add(session_id)

    async def get_session(self, *, session_id: str) -> dict[str, object] | None:
        payload = self.sessions.get(session_id)
        if payload is None:
            return None
        return dict(payload)

    async def delete_session(self, *, session_id: str) -> None:
        self.deleted_sessions.append(session_id)
        payload = self.sessions.pop(session_id, None)
        if payload is None:
            return
        user_id = payload.get("user_id")
        if not isinstance(user_id, str):
            return
        user_session_ids = self.user_sessions.get(user_id)
        if user_session_ids is None:
            return
        user_session_ids.discard(session_id)

    async def delete_user_sessions(self, *, user_id) -> None:  # noqa: ANN001
        normalized_user_id = str(user_id)
        self.deleted_user_sessions.append(normalized_user_id)
        session_ids = set(self.user_sessions.get(normalized_user_id, set()))
        for session_id in session_ids:
            self.sessions.pop(session_id, None)
        self.user_sessions.pop(normalized_user_id, None)


class DummyAuthRepo:
    def __init__(self) -> None:
        self.user_by_email: object | None = None
        self.user_by_email_responses: list[object | None] | None = None
        self.user_by_id: AuthUser | None = None
        self.oauth_account: object | None = None
        self.oauth_account_responses: list[object | None] | None = None
        self.oauth_account_for_user: object | None = None
        self.created_user: AuthUser | None = None
        self.create_user_error: Exception | None = None
        self.create_oauth_account_error: Exception | None = None
        self.create_user_with_oauth_account_error: Exception | None = None
        self.create_user_called_with: tuple[str, str] | None = None
        self.set_password_called_with: tuple[object, str] | None = None
        self.created_oauth_account_calls: list[dict[str, object]] = []
        self.create_user_with_oauth_account_result: tuple[AuthUser, object] | None = None
        self.create_user_with_oauth_account_called_with: dict[str, str] | None = None

    async def get_user_by_email(self, email: str) -> object | None:
        if self.user_by_email_responses is not None and self.user_by_email_responses:
            return self.user_by_email_responses.pop(0)
        return self.user_by_email

    async def create_user(self, email: str, password_hash: str | None) -> AuthUser:
        assert password_hash is not None
        self.create_user_called_with = (email, password_hash)
        if self.create_user_error is not None:
            raise self.create_user_error
        if self.created_user is not None:
            return self.created_user
        return _mk_auth_user(email=email)

    async def get_by_id(self, user_id):  # noqa: ANN001
        return self.user_by_id

    async def set_user_password(self, user_id, password_hash):  # noqa: ANN001
        self.set_password_called_with = (user_id, password_hash)
        return None

    async def set_user_active(self, user_id, is_active):  # noqa: ANN001
        return None

    async def get_oauth_account(
        self,
        provider: str,
        provider_user_id: str,
    ) -> object | None:
        if self.oauth_account_responses is not None and self.oauth_account_responses:
            return self.oauth_account_responses.pop(0)
        return self.oauth_account

    async def get_oauth_account_for_user(
        self,
        user_id,
        provider: str,  # noqa: ANN001
    ) -> object | None:
        return self.oauth_account_for_user

    async def create_oauth_account(
        self,
        *,
        user_id,
        provider: str,  # noqa: ANN001
        provider_user_id: str,
        provider_email: str | None = None,
    ) -> object:
        if self.create_oauth_account_error is not None:
            raise self.create_oauth_account_error
        payload = {
            "user_id": user_id,
            "provider": provider,
            "provider_user_id": provider_user_id,
            "provider_email": provider_email,
        }
        self.created_oauth_account_calls.append(payload)
        return SimpleNamespace(**payload)

    async def create_user_with_oauth_account(
        self,
        *,
        email: str,
        provider: str,
        provider_user_id: str,
    ) -> tuple[AuthUser, object]:
        self.create_user_with_oauth_account_called_with = {
            "email": email,
            "provider": provider,
            "provider_user_id": provider_user_id,
        }
        if self.create_user_with_oauth_account_error is not None:
            raise self.create_user_with_oauth_account_error
        if self.create_user_with_oauth_account_result is not None:
            return self.create_user_with_oauth_account_result
        return _mk_auth_user(email=email), SimpleNamespace()

    async def create_user_with_oauth_account_idempotent(
        self,
        *,
        email: str,
        provider: str,
        provider_user_id: str,
    ) -> tuple[AuthUser, object]:
        normalized_email = email.strip().lower()
        try:
            return await self.create_user_with_oauth_account(
                email=normalized_email,
                provider=provider,
                provider_user_id=provider_user_id,
            )
        except IntegrityError as exc:
            existing_identity = await self.get_oauth_account(provider, provider_user_id)
            if existing_identity:
                linked_user = await self.get_by_id(existing_identity.user_id)
                if linked_user is None:
                    raise

                actual_email = linked_user.email.strip().lower()
                if actual_email != normalized_email:
                    raise OAuthIdentityAlreadyLinkedToAnotherUserError(
                        provider=provider,
                        provider_user_id=provider_user_id,
                    ) from exc

                return linked_user, existing_identity

            existing_user = await self.get_user_by_email(normalized_email)
            if existing_user:
                raise EmailAlreadyExistsError from exc

            raise

    async def create_oauth_account_idempotent(
        self,
        *,
        user_id,
        provider: str,  # noqa: ANN001
        provider_user_id: str,
        provider_email: str | None = None,
    ) -> object:
        try:
            return await self.create_oauth_account(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=provider_email,
            )
        except IntegrityError:
            existing_identity = await self.get_oauth_account(provider, provider_user_id)
            if existing_identity:
                return existing_identity
            raise


def _mk_auth_user(*, email: str = "user@example.com") -> AuthUser:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return AuthUser(
        id=uuid4(),
        email=email,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def _mk_user_model(
    *,
    email: str = "user@example.com",
    is_active: bool = True,
    password_hash: str | None = None,
):
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return SimpleNamespace(
        id=uuid4(),
        email=email,
        is_active=is_active,
        password_hash=password_hash,
        created_at=now,
        updated_at=now,
    )


def test_hash_password_and_verify_password_success() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)

    encoded = service.hash_password("strong-pass-123")
    assert encoded.startswith("$argon2")
    assert service.verify_password("strong-pass-123", encoded) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)

    encoded = service.hash_password("strong-pass-123")
    assert service.verify_password("wrong-pass", encoded) is False


def test_verify_password_returns_false_for_malformed_hash() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)

    ans = service.verify_password("strong-pass-123", "bad-hash")

    assert not ans


def test_verify_password_returns_false_for_invalid_hash_error() -> None:
    class BrokenHasher:
        def verify(self, hash: str, password: str) -> bool:  # noqa: A003
            raise InvalidHashError

    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)
    service.ph = BrokenHasher()  # type: ignore[assignment]

    assert service.verify_password("strong-pass-123", "$argon2$broken") is False


@pytest.mark.asyncio
async def test_register_creates_user_with_hashed_password() -> None:
    repo = DummyAuthRepo()
    repo.created_user = _mk_auth_user(email="user@example.com")
    service = AuthService(auth_repo=repo)

    payload = AuthRegister(email="  USER@Example.com ", password="strong-pass-123")
    created = await service.register(payload)

    assert created == repo.created_user
    assert repo.create_user_called_with is not None
    email, encoded = repo.create_user_called_with
    assert email == "user@example.com"
    assert encoded != payload.password
    assert service.verify_password(payload.password, encoded) is True


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email() -> None:
    repo = DummyAuthRepo()
    repo.user_by_email = _mk_user_model(email="user@example.com", password_hash="x")
    service = AuthService(auth_repo=repo)

    payload = AuthRegister(email="user@example.com", password="strong-pass-123")
    with pytest.raises(EmailAlreadyExistsError):
        await service.register(payload)


@pytest.mark.asyncio
async def test_register_converts_integrity_error_to_duplicate_message() -> None:
    repo = DummyAuthRepo()
    repo.create_user_error = IntegrityError(
        statement="INSERT INTO users ...",
        params={},
        orig=Exception("duplicate"),
    )
    service = AuthService(auth_repo=repo)

    payload = AuthRegister(email="user@example.com", password="strong-pass-123")
    with pytest.raises(EmailAlreadyExistsError):
        await service.register(payload)


@pytest.mark.asyncio
async def test_authenticate_returns_none_for_missing_or_invalid_user() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)

    payload = AuthLogin(email="user@example.com", password="strong-pass-123")
    assert await service.authenticate(payload) is None

    repo.user_by_email = _mk_user_model(
        email="user@example.com",
        is_active=False,
        password_hash=service.hash_password("strong-pass-123"),
    )
    assert await service.authenticate(payload) is None

    repo.user_by_email = _mk_user_model(
        email="user@example.com",
        is_active=True,
        password_hash=None,
    )
    assert await service.authenticate(payload) is None

    repo.user_by_email = _mk_user_model(
        email="user@example.com",
        is_active=True,
        password_hash=service.hash_password("another-password"),
    )
    assert await service.authenticate(payload) is None

    repo.user_by_email = _mk_user_model(
        email="user@example.com",
        is_active=True,
        password_hash="bad-hash",
    )
    assert await service.authenticate(payload) is None


@pytest.mark.asyncio
async def test_set_password_hashes_valid_password_and_calls_repo() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)
    user_id = uuid4()

    await service.set_password(user_id, "strong-pass-123")

    assert repo.set_password_called_with is not None
    saved_user_id, encoded = repo.set_password_called_with
    assert saved_user_id == user_id
    assert encoded != "strong-pass-123"
    assert service.verify_password("strong-pass-123", encoded) is True


@pytest.mark.asyncio
async def test_set_password_rejects_password_that_breaks_policy() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)

    with pytest.raises(ValueError, match="password must be between 8 and 256 characters"):
        await service.set_password(uuid4(), "short")

    assert repo.set_password_called_with is None


@pytest.mark.asyncio
async def test_authenticate_returns_user_for_valid_credentials() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)

    hashed = service.hash_password("strong-pass-123")
    db_user = _mk_user_model(
        email="user@example.com",
        is_active=True,
        password_hash=hashed,
    )
    repo.user_by_email = db_user

    payload = AuthLogin(email="user@example.com", password="strong-pass-123")
    user = await service.authenticate(payload)
    assert user is not None
    assert user.id == db_user.id
    assert user.email == "user@example.com"


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_returns_existing_linked_user() -> None:
    repo = DummyAuthRepo()
    linked_user = _mk_auth_user(email="user@example.com")
    repo.oauth_account = SimpleNamespace(user_id=linked_user.id)
    repo.user_by_id = linked_user
    service = AuthService(auth_repo=repo)

    result = await service.get_or_create_oauth_user(
        email="user@example.com",
        provider="google",
        provider_user_id="google-1",
    )

    assert result == linked_user
    assert repo.create_user_with_oauth_account_called_with is None


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_rejects_existing_email_for_unlinked_oauth() -> None:
    repo = DummyAuthRepo()
    repo.create_user_with_oauth_account_error = IntegrityError(
        statement="INSERT INTO users ...",
        params={},
        orig=Exception("duplicate"),
    )
    repo.user_by_email = _mk_user_model(email="user@example.com", password_hash=None)
    service = AuthService(auth_repo=repo)

    with pytest.raises(EmailAlreadyExistsError):
        await service.get_or_create_oauth_user(
            email="user@example.com",
            provider="google",
            provider_user_id="google-2",
        )

    assert repo.created_oauth_account_calls == []


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_creates_new_user_when_missing() -> None:
    repo = DummyAuthRepo()
    created_user = _mk_auth_user(email="new@example.com")
    repo.create_user_with_oauth_account_result = (created_user, SimpleNamespace())
    service = AuthService(auth_repo=repo)

    result = await service.get_or_create_oauth_user(
        email="new@example.com",
        provider="google",
        provider_user_id="google-3",
    )

    assert result == created_user
    assert repo.create_user_with_oauth_account_called_with == {
        "email": "new@example.com",
        "provider": "google",
        "provider_user_id": "google-3",
    }


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_recovers_from_integrity_race() -> None:
    repo = DummyAuthRepo()
    repo.create_user_with_oauth_account_error = IntegrityError(
        statement="INSERT INTO oauth_accounts ...",
        params={},
        orig=Exception("duplicate"),
    )
    linked_user = _mk_auth_user(email="new@example.com")
    repo.oauth_account_responses = [None, SimpleNamespace(user_id=linked_user.id)]
    repo.user_by_id = linked_user
    service = AuthService(auth_repo=repo)

    result = await service.get_or_create_oauth_user(
        email="new@example.com",
        provider="google",
        provider_user_id="google-race",
    )

    assert result == linked_user


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_rejects_integrity_race_for_another_user() -> None:
    repo = DummyAuthRepo()
    repo.create_user_with_oauth_account_error = IntegrityError(
        statement="INSERT INTO oauth_accounts ...",
        params={},
        orig=Exception("duplicate"),
    )
    linked_user = _mk_auth_user(email="other@example.com")
    repo.oauth_account_responses = [None, SimpleNamespace(user_id=linked_user.id)]
    repo.user_by_id = linked_user
    service = AuthService(auth_repo=repo)

    with pytest.raises(OAuthIdentityAlreadyLinkedToAnotherUserError):
        await service.get_or_create_oauth_user(
            email="new@example.com",
            provider="google",
            provider_user_id="google-race",
        )


@pytest.mark.asyncio
async def test_get_or_create_oauth_user_converts_email_integrity_race_to_domain_error() -> None:
    repo = DummyAuthRepo()
    repo.create_user_with_oauth_account_error = IntegrityError(
        statement="INSERT INTO users ...",
        params={},
        orig=Exception("duplicate"),
    )
    repo.user_by_email = _mk_user_model(email="new@example.com", password_hash=None)
    service = AuthService(auth_repo=repo)

    with pytest.raises(EmailAlreadyExistsError):
        await service.get_or_create_oauth_user(
            email="new@example.com",
            provider="google",
            provider_user_id="google-email-race",
        )


@pytest.mark.asyncio
async def test_link_oauth_account_for_user_creates_new_link() -> None:
    repo = DummyAuthRepo()
    service = AuthService(auth_repo=repo)
    user_id = uuid4()

    created = await service.link_oauth_account_for_user(
        user_id=user_id,
        provider="google",
        provider_user_id="google-10",
        provider_email="user@example.com",
    )

    assert len(repo.created_oauth_account_calls) == 1
    payload = repo.created_oauth_account_calls[0]
    assert payload["user_id"] == user_id
    assert payload["provider"] == "google"
    assert payload["provider_user_id"] == "google-10"
    assert payload["provider_email"] == "user@example.com"
    assert created.provider_user_id == "google-10"


@pytest.mark.asyncio
async def test_link_oauth_account_for_user_returns_existing_link_for_same_user() -> None:
    repo = DummyAuthRepo()
    user_id = uuid4()
    existing = SimpleNamespace(
        user_id=user_id,
        provider="google",
        provider_user_id="google-11",
    )
    repo.oauth_account = existing
    service = AuthService(auth_repo=repo)

    result = await service.link_oauth_account_for_user(
        user_id=user_id,
        provider="google",
        provider_user_id="google-11",
    )

    assert result is existing
    assert repo.created_oauth_account_calls == []


@pytest.mark.asyncio
async def test_link_oauth_account_for_user_rejects_identity_linked_to_other_user() -> None:
    repo = DummyAuthRepo()
    repo.oauth_account = SimpleNamespace(
        user_id=uuid4(),
        provider="google",
        provider_user_id="google-12",
    )
    service = AuthService(auth_repo=repo)

    with pytest.raises(OAuthIdentityAlreadyLinkedToAnotherUserError):
        await service.link_oauth_account_for_user(
            user_id=uuid4(),
            provider="google",
            provider_user_id="google-12",
        )


@pytest.mark.asyncio
async def test_link_oauth_account_for_user_rejects_second_account_for_provider() -> None:
    repo = DummyAuthRepo()
    user_id = uuid4()
    repo.oauth_account_for_user = SimpleNamespace(
        user_id=user_id,
        provider="google",
        provider_user_id="google-old",
    )
    service = AuthService(auth_repo=repo)

    with pytest.raises(ProviderAccountAlreadyLinkedError):
        await service.link_oauth_account_for_user(
            user_id=user_id,
            provider="google",
            provider_user_id="google-new",
        )


@pytest.mark.asyncio
async def test_link_oauth_account_for_user_recovers_from_integrity_race() -> None:
    repo = DummyAuthRepo()
    user_id = uuid4()
    repo.create_oauth_account_error = IntegrityError(
        statement="INSERT INTO oauth_accounts ...",
        params={},
        orig=Exception("duplicate"),
    )
    existing = SimpleNamespace(
        user_id=user_id,
        provider="google",
        provider_user_id="google-13",
    )
    repo.oauth_account_responses = [None, existing]
    service = AuthService(auth_repo=repo)

    result = await service.link_oauth_account_for_user(
        user_id=user_id,
        provider="google",
        provider_user_id="google-13",
    )

    assert result is existing


@pytest.mark.asyncio
async def test_link_oauth_account_for_user_rejects_integrity_race_for_other_user() -> None:
    repo = DummyAuthRepo()
    user_id = uuid4()
    repo.create_oauth_account_error = IntegrityError(
        statement="INSERT INTO oauth_accounts ...",
        params={},
        orig=Exception("duplicate"),
    )
    repo.oauth_account_responses = [
        None,
        SimpleNamespace(
            user_id=uuid4(),
            provider="google",
            provider_user_id="google-14",
        ),
    ]
    service = AuthService(auth_repo=repo)

    with pytest.raises(OAuthIdentityAlreadyLinkedToAnotherUserError):
        await service.link_oauth_account_for_user(
            user_id=user_id,
            provider="google",
            provider_user_id="google-14",
        )


@pytest.mark.asyncio
async def test_login_create_session_creates_payload_and_returns_session_id() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    fixed_now = datetime(2026, 3, 8, 12, 0, tzinfo=UTC)
    service = AuthService(
        auth_repo=repo,
        session_store=store,
        session_ttl_seconds=600,
        now_provider=lambda: fixed_now,
    )
    user_id = uuid4()

    session_id = await service.login_create_session(user_id=user_id)

    assert session_id in store.sessions
    assert store.sessions[session_id]["user_id"] == str(user_id)
    assert store.sessions[session_id]["created_at"] == "2026-03-08T12:00:00Z"
    assert store.sessions[session_id]["expires_at"] == "2026-03-08T12:10:00Z"


@pytest.mark.asyncio
async def test_logout_deletes_single_session() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    service = AuthService(auth_repo=repo, session_store=store)
    session_id = "sess-logout"
    user_id = uuid4()
    store.sessions[session_id] = {"user_id": str(user_id)}

    await service.logout(session_id=session_id, user_id=user_id)

    assert session_id not in store.sessions
    assert session_id in store.deleted_sessions


@pytest.mark.asyncio
async def test_logout_does_not_delete_other_users_session() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    service = AuthService(auth_repo=repo, session_store=store)
    session_id = "sess-foreign"
    store.sessions[session_id] = {"user_id": str(uuid4())}

    await service.logout(session_id=session_id, user_id=uuid4())

    assert session_id in store.sessions
    assert session_id not in store.deleted_sessions


@pytest.mark.asyncio
async def test_logout_all_deletes_all_user_sessions() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    service = AuthService(auth_repo=repo, session_store=store)
    user_id = uuid4()
    other_user_id = uuid4()
    store.user_sessions[str(user_id)] = {"sess-1", "sess-2"}
    store.user_sessions[str(other_user_id)] = {"sess-3"}
    store.sessions["sess-1"] = {"user_id": str(user_id)}
    store.sessions["sess-2"] = {"user_id": str(user_id)}
    store.sessions["sess-3"] = {"user_id": str(other_user_id)}

    await service.logout_all(user_id=user_id)

    assert "sess-1" not in store.sessions
    assert "sess-2" not in store.sessions
    assert "sess-3" in store.sessions
    assert str(user_id) not in store.user_sessions
    assert str(user_id) in store.deleted_user_sessions


@pytest.mark.asyncio
async def test_resolve_user_returns_user_for_valid_session() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    fixed_now = datetime(2026, 3, 8, 12, 0, tzinfo=UTC)
    service = AuthService(
        auth_repo=repo,
        session_store=store,
        now_provider=lambda: fixed_now,
    )
    user = _mk_auth_user(email="session-user@example.com")
    repo.user_by_id = user
    session_id = "sess-valid"
    store.sessions[session_id] = {
        "user_id": str(user.id),
        "created_at": "2026-03-08T11:50:00Z",
        "expires_at": "2026-03-08T12:30:00Z",
    }

    resolved = await service.resolve_user(session_id=session_id)

    assert resolved == user


@pytest.mark.asyncio
async def test_resolve_user_returns_none_for_missing_session() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    service = AuthService(auth_repo=repo, session_store=store)

    assert await service.resolve_user(session_id="sess-missing") is None


@pytest.mark.asyncio
async def test_resolve_user_returns_none_and_revokes_expired_session() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    fixed_now = datetime(2026, 3, 8, 12, 0, tzinfo=UTC)
    service = AuthService(
        auth_repo=repo,
        session_store=store,
        now_provider=lambda: fixed_now,
    )
    user = _mk_auth_user(email="expired-user@example.com")
    repo.user_by_id = user
    session_id = "sess-expired"
    store.sessions[session_id] = {
        "user_id": str(user.id),
        "created_at": "2026-03-08T10:00:00Z",
        "expires_at": "2026-03-08T11:59:59Z",
    }

    resolved = await service.resolve_user(session_id=session_id)

    assert resolved is None
    assert session_id in store.deleted_sessions
    assert session_id not in store.sessions


@pytest.mark.asyncio
async def test_resolve_user_returns_none_and_revokes_revoked_session() -> None:
    repo = DummyAuthRepo()
    store = DummySessionStore()
    service = AuthService(auth_repo=repo, session_store=store)
    session_id = "sess-revoked"
    store.sessions[session_id] = {
        "user_id": str(uuid4()),
        "created_at": "2026-03-08T10:00:00Z",
        "expires_at": "2026-03-08T12:30:00Z",
        "revoked_at": "2026-03-08T11:00:00Z",
    }

    resolved = await service.resolve_user(session_id=session_id)

    assert resolved is None
    assert session_id in store.deleted_sessions
    assert session_id not in store.sessions
