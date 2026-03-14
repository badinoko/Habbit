import httpx

from src.config import settings
from src.schemas import ZenquoteAPI


class ZenQuotesService:
    def __init__(self, http_client: httpx.AsyncClient):
        self._http_client = http_client

    async def fetch_batch(self) -> list[ZenquoteAPI]:
        response = await self._http_client.get(
            settings.ZENQUOTES_API_URL,
            timeout=10.0,
        )
        response.raise_for_status()
        return [ZenquoteAPI.model_validate(item) for item in response.json()]
