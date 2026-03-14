from uuid import UUID

from src.database.models.quotes import QuoteBatch as QuoteBatchORM, TaskStatus
from src.schemas import QuoteBatch, QuoteBatchInDB, QuoteBatchUpdate

from .base import GenericSqlRepository


class QuoteBatchRepository(
    GenericSqlRepository[
        QuoteBatch,
        QuoteBatchInDB,
        QuoteBatchUpdate,
        QuoteBatchORM,
        UUID,
    ]
):
    _model = QuoteBatchORM
    _create_schema = QuoteBatch
    _read_schema = QuoteBatchInDB
    _update_schema = QuoteBatchUpdate

    async def create_pending_batch(self) -> QuoteBatchInDB:
        return await self.add(
            QuoteBatch(
                source="zenquotes",
                status=TaskStatus.pending,
            )
        )

    async def activate_batch(self, batch_id: UUID) -> QuoteBatchInDB | None:
        return await self.update(
            batch_id,
            QuoteBatchUpdate(status=TaskStatus.active),
        )

    async def fail_batch(self, batch_id: UUID) -> QuoteBatchInDB | None:
        return await self.update(
            batch_id,
            QuoteBatchUpdate(status=TaskStatus.inactive),
        )
