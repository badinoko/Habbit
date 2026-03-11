from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import ColumnElement, delete as sa_delete, false, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import SQLColumnExpression

from src.database.models import OwnedModel
from src.repositories.base import (
    CreateType,
    GenericSqlRepository,
    IdType,
    ReadType,
    UpdateType,
)

OwnedModelType = TypeVar("OwnedModelType", bound=OwnedModel)


class OwnedRepository(
    GenericSqlRepository[
        CreateType,
        ReadType,
        UpdateType,
        OwnedModelType,
        IdType,
    ]
):
    """
    Базовый request-scoped репозиторий для owner-scoped моделей.

    Репозиторий всегда работает в контексте конкретного пользователя и обязан
    строить owner-фильтрацию через `_owner_filter()` / `_apply_owner_scope()`.

    Любые кастомные запросы в наследниках должны использовать эти helper-методы,
    а не сравнивать `model.owner_id == self._owner_id` напрямую, потому что в
    SQL такое сравнение с `None` превращается в `IS NULL`.
    """

    def __init__(self, session: AsyncSession, owner_id: UUID | None) -> None:
        super().__init__(session)
        self._owner_id = owner_id

    def _owner_filter(self, column: SQLColumnExpression[Any]) -> ColumnElement[bool]:
        if self._owner_id is None:
            return false()
        return column == self._owner_id

    def _apply_owner_scope(
        self, stmt: Select[tuple[OwnedModelType]]
    ) -> Select[tuple[OwnedModelType]]:
        return stmt.where(self._owner_filter(self._model.owner_id))

    def _construct_get_stmt(self, id: IdType) -> Select[tuple[OwnedModelType]]:
        return self._apply_owner_scope(select(self._model).where(self._model.id == id))

    def _construct_list_stmt(
        self, *options: ExecutableOption, **filters: object
    ) -> Select[tuple[OwnedModelType]]:
        return self._apply_owner_scope(
            super()._construct_list_stmt(*options, **filters)
        )

    def _convert_create_to_model(self, obj: CreateType) -> OwnedModelType:
        record = super()._convert_create_to_model(obj)
        if self._owner_id is None:
            raise RuntimeError("Authentication required")
        record.owner_id = self._owner_id
        return record

    async def get_by_id(self, id: IdType) -> ReadType | None:
        stmt = self._construct_get_stmt(id)
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return self._convert_model_to_read(record)

    async def update(self, id: IdType, obj: UpdateType) -> ReadType | None:
        stmt = self._construct_get_stmt(id)
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return None

        self._convert_update_to_model(obj, record)
        await self._session.flush()
        return self._convert_model_to_read(record)

    async def delete(self, id: IdType) -> bool:
        stmt = sa_delete(self._model).where(
            self._model.id == id,
            self._owner_filter(self._model.owner_id),
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0
