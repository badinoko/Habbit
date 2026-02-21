# mypy: ignore-errors
import logging
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.base import ExecutableOption

from src.database.models import BaseModel as SQLBase
from src.schemas.base import InDBBase

# Параметризуем тип ID, чтобы репозиторий можно было использовать с int, UUID, str и т.д.
IdType = TypeVar("IdType", int, UUID, str)

CreateType = TypeVar("CreateType", bound=BaseModel)
ReadType = TypeVar("ReadType", bound=InDBBase)
UpdateType = TypeVar("UpdateType", bound=BaseModel)
ModelType = TypeVar("ModelType", bound=SQLBase)

logger = logging.getLogger(__name__)


class GenericSqlRepository[CreateType, ReadType, UpdateType, ModelType, IdType]:
    """
    Базовый класс для SQL-репозиториев с полной типизацией.

    :param CreateType: Pydantic-схема для создания записи (без id, created_at, updated_at)
    :param ReadType: Pydantic-схема для чтения записи из БД (включает все поля)
    :param UpdateType: Pydantic-схема для обновления записи (все поля опциональны)
    :param ModelType: класс SQLAlchemy модели
    :param IdType: тип поля первичного ключа (int, UUID, str и т.д.)
    """

    _model: type[ModelType]
    _create_schema: type[CreateType]
    _read_schema: type[ReadType]
    _update_schema: type[UpdateType]

    def __init__(self, session: AsyncSession) -> None:
        if not hasattr(self, "_model"):
            raise NotImplementedError("_model must be defined in subclass")
        if not hasattr(self, "_create_schema"):
            raise NotImplementedError("_create_schema must be defined in subclass")
        if not hasattr(self, "_read_schema"):
            raise NotImplementedError("_read_schema must be defined in subclass")
        if not hasattr(self, "_update_schema"):
            raise NotImplementedError("_update_schema must be defined in subclass")
        self._session = session

    # ========== Вспомогательные методы для построения запросов ==========
    def _construct_get_stmt(self, id: IdType) -> Select[tuple[ModelType]]:
        """Строит SELECT запрос для получения записи по ID."""
        return select(self._model).where(self._model.id == id)

    def _construct_list_stmt(
        self, *options: ExecutableOption, **filters: object
    ) -> Select[tuple[ModelType]]:
        """
        Строит SELECT запрос с фильтрацией по переданным именованным параметрам.
        Имена параметров должны соответствовать колонкам модели.

        :param options: Дополнительные опции загрузки (joinedload, selectinload и т.д.)
        :param filters: Фильтры в виде равенств по колонкам.
        """
        stmt = select(self._model)
        if options:
            stmt = stmt.options(*options)

        where_clauses = []
        for column, value in filters.items():
            if not hasattr(self._model, column):
                raise ValueError(
                    f"Invalid column name '{column}' for model {self._model.__name__}"
                )
            where_clauses.append(getattr(self._model, column) == value)

        if where_clauses:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    # ========== Преобразования между схемами и моделями ==========
    def _convert_create_to_model(self, obj: CreateType) -> ModelType:
        """Создаёт экземпляр модели из схемы создания."""
        data = obj.model_dump()
        return self._model(**data)

    def _convert_update_to_model(self, obj: UpdateType, record: ModelType) -> None:
        """
        Обновляет существующую модель данными из схемы обновления.
        Использует только явно переданные поля (exclude_unset=True).
        """
        update_data = obj.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

    def _convert_model_to_read(self, record: ModelType) -> ReadType:
        """Создаёт схему чтения из экземпляра модели."""
        return self._read_schema.model_validate(record, from_attributes=True)

    # ========== Основные методы ==========
    async def get_by_id(self, id: IdType) -> ReadType | None:
        """
        Возвращает запись по ID или None, если не найдена.
        """
        # Используем session.get вместо явного SELECT для эффективности
        record = await self._session.get(self._model, id)
        if record is None:
            return None
        return self._convert_model_to_read(record)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        *options: ExecutableOption,
        **filters: object,
    ) -> list[ReadType]:
        """
        Возвращает список записей с пагинацией, фильтрацией и опциями загрузки.

        :param skip: Количество пропускаемых записей.
        :param limit: Максимальное количество возвращаемых записей.
        :param options: Опции загрузки (например, joinedload(Theme.questions)).
        :param filters: Фильтры в виде равенств по колонкам.
        """
        stmt = self._construct_list_stmt(*options, **filters)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        records = (
            result.scalars().unique().all()
        )  # unique() важен при использовании joinedload
        return [self._convert_model_to_read(rec) for rec in records]

    async def add(self, obj: CreateType) -> ReadType:
        """Создаёт новую запись из схемы создания и возвращает прочитанную из БД."""
        record = self._convert_create_to_model(obj)
        self._session.add(record)
        await self._session.flush()  # получаем ID и значения по умолчанию
        # await self._session.refresh(record)  # Если у моделей есть server_default эта строка нужна
        return self._convert_model_to_read(record)

    async def update(self, id: IdType, obj: UpdateType) -> ReadType | None:
        """
        Обновляет существующую запись данными из схемы обновления.
        Возвращает обновлённую запись или None, если запись не найдена.
        """
        # Получаем модель одним запросом
        record = await self._session.get(self._model, id)
        if record is None:
            return None

        # Применяем изменения
        self._convert_update_to_model(obj, record)
        await self._session.flush()

        return self._convert_model_to_read(record)

    async def delete(self, id: IdType) -> bool:
        """
        Удаляет запись по ID.
        Возвращает True, если запись была удалена, иначе False.
        """
        stmt = sa_delete(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        await self._session.flush()

        return result.rowcount > 0
