import logging

import httpx

from src.config import settings
from src.schemas import ZenquoteAPI

logger = logging.getLogger(__name__)


class ZenQuotesService:
    def __init__(self, http_client: httpx.AsyncClient):
        self._http_client = http_client

    async def fetch_batch(self) -> list[ZenquoteAPI]:
        try:
            response = await self._http_client.get(
                settings.ZENQUOTES_API_URL,
                timeout=10.0,
            )
            response.raise_for_status()
            return [ZenquoteAPI.model_validate(item) for item in response.json()]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("ZenQuotes returned 429 Too Many Requests")
                return []
            raise
