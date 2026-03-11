import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final
from uuid import UUID, uuid4

import httpx
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy.exc import IntegrityError

from src.config import settings
from src.exceptions import (
    EmailAlreadyExistsError,
    GoogleOauthError,
    OAuthAuthorizationCodeMissingError,
    OAuthConfigurationError,
    OAuthEmailNotVerifiedError,
    OAuthIdentityAlreadyLinkedToAnotherUserError,
    OAuthProviderRejectedError,
    OAuthProviderUnavailableError,
    OAuthStateInvalidError,
    ProviderAccountAlreadyLinkedError,
    UserIsInactiveError,
)
from src.repositories import AuthRepository
from src.repositories.session_store import RedisSessionStore
from src.schemas.auth import (
    AuthLogin,
    AuthRegister,
    AuthUser,
    OAuthAccountRead,
)
from src.services.google_oauth import GoogleOauth


@dataclass(frozen=True)
class GoogleOauthStartFlow:
    authorization_url: str
    session_payload: dict[str, str]


@dataclass(frozen=True)
class GoogleOauthLoginResult:
    next_url: str
    session_id: str
    user: AuthUser


class AuthService:
    """Сервис авторизации: локальный вход/регистрация и OAuth-связки."""

    ph = PasswordHasher()
    _SESSION_STORE_NOT_CONFIGURED: Final[str] = (
        "Session store is not configured for auth sessions"
    )

    def __init__(
        self,
        auth_repo: AuthRepository,
        session_store: RedisSessionStore | None = None,
        session_ttl_seconds: int = settings.AUTH_SESSION_MAX_AGE,
        google_oauth_state_ttl_seconds: int = settings.GOOGLE_OAUTH_STATE_TTL,
        http_client: httpx.AsyncClient | None = None,
        google_oauth_client_factory: Callable[[], GoogleOauth] | None = None,
        state_token_provider: Callable[[], str] | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ):
        """Инициализировать сервис с репозиторием авторизации."""
        self.auth_repo = auth_repo
        self._session_store = session_store
        self._session_ttl_seconds = session_ttl_seconds
        self._google_oauth_state_ttl_seconds = google_oauth_state_ttl_seconds
        self._http_client = http_client
        self._google_oauth_client_factory = google_oauth_client_factory
        self._state_token_provider = state_token_provider or (
            lambda: secrets.token_urlsafe(32)
        )
        self._now_provider = now_provider or (lambda: datetime.now(UTC))

    @staticmethod
    def _format_datetime(value: datetime) -> str:
        return (
            value.astimezone(UTC)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _normalize_next(next_value: object) -> str:
        if not isinstance(next_value, str) or not next_value:
            return "/"

        from urllib.parse import urlsplit

        parsed = urlsplit(next_value)
        if parsed.scheme or parsed.netloc:
            return "/"
        if not next_value.startswith("/") or next_value.startswith("//"):
            return "/"
        return next_value

    def _require_session_store(self) -> RedisSessionStore:
        if self._session_store is None:
            raise RuntimeError(self._SESSION_STORE_NOT_CONFIGURED)
        return self._session_store

    def _build_google_oauth_client(self) -> GoogleOauth:
        if self._google_oauth_client_factory is not None:
            return self._google_oauth_client_factory()

        if not settings.google_oauth_enabled:
            raise OAuthConfigurationError("Google OAuth is not configured")
        return GoogleOauth(
            client_id=str(settings.GOOGLE_OAUTH_CLIENT_ID),
            client_secret=str(settings.GOOGLE_OAUTH_CLIENT_SECRET),
            redirect_uri=str(settings.GOOGLE_OAUTH_REDIRECT_URI),
            http_client=self._http_client,
        )

    def start_google_oauth_login(self, *, next_url: str) -> GoogleOauthStartFlow:
        state = self._state_token_provider()
        if not state:
            raise ValueError("state_token_provider must return a non-empty state")

        session_payload = {
            "state": state,
            "next": self._normalize_next(next_url),
            "issued_at": self._format_datetime(self._now_provider()),
        }
        authorization_url = self._build_google_oauth_client().get_authorization_url(
            state=state
        )
        return GoogleOauthStartFlow(
            authorization_url=authorization_url,
            session_payload=session_payload,
        )

    async def complete_google_oauth_login(
        self,
        *,
        oauth_session: object,
        provided_state: object,
        provider_error: object,
        code: object,
    ) -> GoogleOauthLoginResult:
        next_url = "/"
        expected_state: str | None = None
        issued_at: datetime | None = None
        if isinstance(oauth_session, dict):
            next_url = self._normalize_next(oauth_session.get("next"))
            stored_state = oauth_session.get("state")
            if isinstance(stored_state, str) and stored_state:
                expected_state = stored_state
            issued_at = self._parse_datetime(oauth_session.get("issued_at"))

        now = self._now_provider()
        state_deadline = None
        if issued_at is not None:
            state_deadline = issued_at + timedelta(
                seconds=self._google_oauth_state_ttl_seconds
            )

        if (
            not isinstance(provided_state, str)
            or not provided_state
            or expected_state is None
            or issued_at is None
            or state_deadline is None
            or state_deadline <= now
            or not secrets.compare_digest(expected_state, provided_state)
        ):
            raise OAuthStateInvalidError

        if isinstance(provider_error, str) and provider_error:
            raise OAuthProviderRejectedError

        if not isinstance(code, str) or not code:
            raise OAuthAuthorizationCodeMissingError

        try:
            identity = await self._build_google_oauth_client().authenticate(code)
        except GoogleOauthError as exc:
            raise OAuthProviderUnavailableError from exc

        if not identity.email_verified:
            raise OAuthEmailNotVerifiedError

        user = await self.get_or_create_oauth_user(
            email=str(identity.email),
            provider="google",
            provider_user_id=identity.provider_user_id,
        )
        session_id = await self.login_create_session(user.id)
        return GoogleOauthLoginResult(
            next_url=next_url,
            session_id=session_id,
            user=user,
        )

    async def login_create_session(self, user_id: UUID) -> str:
        """Создать auth-сессию и вернуть её идентификатор."""
        store = self._require_session_store()
        if self._session_ttl_seconds <= 0:
            raise ValueError("session_ttl_seconds must be greater than zero")

        created_at = self._now_provider()
        expires_at = created_at + timedelta(seconds=self._session_ttl_seconds)
        session_id = str(uuid4())
        await store.create_session(
            session_id=session_id,
            user_id=user_id,
            payload={
                "created_at": self._format_datetime(created_at),
                "expires_at": self._format_datetime(expires_at),
            },
            ttl_seconds=self._session_ttl_seconds,
        )
        return session_id

    async def logout(self, session_id: str, user_id: UUID) -> None:
        """Завершить одну auth-сессию пользователя, если она ему принадлежит."""
        store = self._require_session_store()
        session_payload = await store.get_session(session_id=session_id)
        if session_payload is None:
            return

        payload_user_id = session_payload.get("user_id")
        if not isinstance(payload_user_id, str):
            await store.delete_session(session_id=session_id)
            return

        try:
            session_user_id = UUID(payload_user_id)
        except ValueError:
            await store.delete_session(session_id=session_id)
            return

        if session_user_id != user_id:
            return

        await store.delete_session(session_id=session_id)

    async def logout_all(self, user_id: UUID) -> None:
        """Завершить все auth-сессии пользователя."""
        store = self._require_session_store()
        await store.delete_user_sessions(user_id=user_id)

    async def resolve_user(self, session_id: str) -> AuthUser | None:
        """Разрешить пользователя по session_id или вернуть None."""
        store = self._require_session_store()
        session_payload = await store.get_session(session_id=session_id)
        if session_payload is None:
            return None

        if session_payload.get("revoked") or session_payload.get("revoked_at"):
            await store.delete_session(session_id=session_id)
            return None

        expires_at = self._parse_datetime(session_payload.get("expires_at"))
        now = self._now_provider()
        if expires_at is not None and expires_at <= now:
            await store.delete_session(session_id=session_id)
            return None

        user_id_raw = session_payload.get("user_id")
        if not isinstance(user_id_raw, str):
            await store.delete_session(session_id=session_id)
            return None

        try:
            user_id = UUID(user_id_raw)
        except ValueError:
            await store.delete_session(session_id=session_id)
            return None

        user = await self.auth_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            await store.delete_session(session_id=session_id)
            return None
        return user

    async def register(self, payload: AuthRegister) -> AuthUser:
        """Зарегистрировать пользователя по email/паролю."""
        existing = await self.auth_repo.get_user_by_email(payload.email)
        if existing:
            raise EmailAlreadyExistsError

        try:
            return await self.auth_repo.create_user(
                payload.email,
                self.hash_password(payload.password),
            )
        except IntegrityError as exc:
            raise EmailAlreadyExistsError from exc

    async def authenticate(self, payload: AuthLogin) -> AuthUser | None:
        """Проверить логин/пароль и вернуть пользователя при успехе."""
        user = await self.auth_repo.get_user_by_email(payload.email)
        if not user or not user.is_active or not user.password_hash:
            return None
        if not self.verify_password(payload.password, user.password_hash):
            return None
        return AuthUser.model_validate(user)

    async def get_user(self, user_id: UUID) -> AuthUser | None:
        """Получить пользователя по идентификатору."""
        return await self.auth_repo.get_by_id(user_id)

    async def set_password(self, user_id: UUID, password: str) -> AuthUser | None:
        """Обновить пароль пользователя."""
        validated_password = AuthRegister.validate_password(password)
        return await self.auth_repo.set_user_password(
            user_id, self.hash_password(validated_password)
        )

    async def set_user_active(self, user_id: UUID, is_active: bool) -> AuthUser | None:
        """Изменить статус активности пользователя."""
        return await self.auth_repo.set_user_active(user_id, is_active)

    async def get_or_create_oauth_user(
        self,
        *,
        email: str,
        provider: str,
        provider_user_id: str,
    ) -> AuthUser:
        """
        Вернуть пользователя по OAuth-связке или создать нового.
        Автопривязка к существующему пользователю по email отключена из соображений безопасности.
        """
        normalized_email = email.strip().lower()

        account = await self.auth_repo.get_oauth_account(provider, provider_user_id)
        if account:
            linked_user = await self.auth_repo.get_by_id(account.user_id)
            if linked_user and linked_user.is_active:
                return linked_user
            elif linked_user and not linked_user.is_active:
                raise UserIsInactiveError

        try:
            (
                created_user,
                _,
            ) = await self.auth_repo.create_user_with_oauth_account_idempotent(
                email=normalized_email,
                provider=provider,
                provider_user_id=provider_user_id,
            )
            return created_user
        except (EmailAlreadyExistsError, OAuthIdentityAlreadyLinkedToAnotherUserError):
            raise

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, password: str, hash: str) -> bool:
        try:
            return self.ph.verify(hash, password)
        except (VerificationError, InvalidHashError):
            return False

    async def create_oauth_account(
        self,
        *,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
        provider_email: str | None = None,
    ) -> OAuthAccountRead:
        """Создать OAuth-аккаунт для существующего пользователя."""
        return await self.auth_repo.create_oauth_account(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
        )

    async def link_oauth_account_for_user(
        self,
        *,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
        provider_email: str | None = None,
    ) -> OAuthAccountRead:
        """Привязать OAuth-аккаунт к уже аутентифицированному пользователю."""
        existing_identity = await self.auth_repo.get_oauth_account(
            provider, provider_user_id
        )
        if existing_identity:
            if existing_identity.user_id != user_id:
                raise OAuthIdentityAlreadyLinkedToAnotherUserError(
                    provider=provider, provider_user_id=provider_user_id
                )
            return existing_identity

        existing_provider_link = await self.auth_repo.get_oauth_account_for_user(
            user_id, provider
        )
        if existing_provider_link:
            if existing_provider_link.provider_user_id != provider_user_id:
                raise ProviderAccountAlreadyLinkedError
            return existing_provider_link

        linked_identity = await self.auth_repo.create_oauth_account_idempotent(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
        )
        if linked_identity.user_id != user_id:
            raise OAuthIdentityAlreadyLinkedToAnotherUserError(
                provider=provider, provider_user_id=provider_user_id
            )
        return linked_identity
