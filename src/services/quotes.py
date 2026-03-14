import random
from uuid import UUID

from src.repositories.quote_batches import QuoteBatchRepository
from src.repositories.quotes import QuoteRepository
from src.schemas import QuoteAnswer
from src.services.zen_quote import ZenQuotesService

FALLBACK_QUOTES = [
    QuoteAnswer(text="Stay hungry, stay foolish.", author="Steve Jobs"),
    QuoteAnswer(
        text="Simplicity is the soul of efficiency.",
        author="Austin Freeman",
    ),
]


class QuoteService:
    def __init__(
        self,
        batch_repository: QuoteBatchRepository,
        quote_repository: QuoteRepository,
        zenquotes_service: ZenQuotesService,
    ):
        self._batch_repository = batch_repository
        self._quote_repository = quote_repository
        self._zenquotes_service = zenquotes_service

    async def refresh_quotes_batch(self) -> UUID:
        batch = await self._batch_repository.create_pending_batch()

        try:
            quotes = await self._zenquotes_service.fetch_batch()
            await self._quote_repository.insert_quotes(batch.id, quotes)
            await self._batch_repository.activate_batch(batch.id)
        except Exception:
            await self._batch_repository.fail_batch(batch.id)
            raise

        return batch.id

    async def get_random_quote(self) -> QuoteAnswer:
        quote = await self._quote_repository.get_random_quote_from_ready_batch()
        if quote is None:
            return random.choice(FALLBACK_QUOTES)
        return quote
