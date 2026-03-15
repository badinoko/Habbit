from uuid import UUID

from sqlalchemy import func, select

from src.database.models.quotes import Quote, QuoteBatch, TaskStatus
from src.schemas import QuoteAnswer, QuoteCreate, QuoteInDB, QuoteUpdate, ZenquoteAPI

from .base import GenericSqlRepository


class QuoteRepository(
    GenericSqlRepository[
        QuoteCreate,
        QuoteInDB,
        QuoteUpdate,
        Quote,
        UUID,
    ]
):
    _model = Quote
    _create_schema = QuoteCreate
    _read_schema = QuoteInDB
    _update_schema = QuoteUpdate

    async def insert_quotes(
        self, batch_id: UUID, quotes: list[ZenquoteAPI]
    ) -> list[QuoteInDB]:
        records = [
            self._model(
                batch_id=batch_id,
                text=quote.text,
                author=quote.author,
                lang="en",
            )
            for quote in quotes
        ]
        self._session.add_all(records)
        await self._session.flush()
        return [self._convert_model_to_read(record) for record in records]

    async def get_random_quote_from_ready_batch(self) -> QuoteAnswer | None:
        stmt = (
            select(Quote)
            .join(QuoteBatch, Quote.batch_id == QuoteBatch.id)
            .where(QuoteBatch.status == TaskStatus.active)
            .order_by(func.random())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return QuoteAnswer.model_validate(record, from_attributes=True)
