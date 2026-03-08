class AppException(Exception):
    """Базовое исключение приложения"""

    pass


class RedisConnectionException(AppException):
    """Ошибка подключения к Redis"""

    pass


class DatabaseException(AppException):
    """Ошибка работы с базой данных"""

    pass


class ValidationException(AppException):
    """Ошибка валидации данных"""

    pass


class EntityNotFound(AppException):
    """Ошибка: сущность не найдена"""

    pass


class TaskNotFound(EntityNotFound):
    """Ошибка: задача не найдена"""

    pass


class HabitNotFound(EntityNotFound):
    """Ошибка: привычка не найдена"""

    pass


class OAuthIdentityAlreadyLinkedToAnotherUserError(DatabaseException):
    """OAuth-идентификатор уже привязан к другому пользователю."""

    __slots__ = ("provider", "provider_user_id")

    def __init__(self, *, provider: str, provider_user_id: str) -> None:
        self.provider = provider
        self.provider_user_id = provider_user_id
        super().__init__(
            f"OAuth identity '{provider}:{provider_user_id}' is already linked to another user"
        )


class EmailAlreadyExistsError(DatabaseException):
    "Пользователь с таким email уже сущестсвует в БД"

    pass


class UserIsInactiveError(AppException):
    "Пользователь помечен как неактивный"

    pass


class ProviderAccountAlreadyLinkedError(AppException):
    "User already has a different linked account for provider"

    pass
