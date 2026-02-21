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
