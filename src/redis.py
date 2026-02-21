import asyncio
import logging
from types import TracebackType
from typing import Any, Self, cast

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError

from src.config import settings

logger = logging.getLogger(__name__)


class RedisAdapter:
    def __init__(self) -> None:
        self.dsn = settings.redis.dsn  # type: ignore # TODO добавить в конфиг
        self._redis: Redis | None = None  # указываем тип
        self._retry_attempts = 3
        self._retry_delay = 1

    async def _get_connection(self) -> Redis:
        for attempt in range(self._retry_attempts):
            try:
                if self._redis is None:
                    self._redis = Redis.from_url(
                        self.dsn,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_keepalive=True,
                        retry_on_timeout=True,
                        socket_timeout=5,
                    )

                # после проверки self._redis точно не None
                assert self._redis is not None
                if not await self._redis.ping():  # type: ignore[misc]
                    await self._redis.aclose()
                    self._redis = None
                    raise ConnectionError("Redis connection failed")
                return self._redis
            except (RedisError, ConnectionError) as e:
                if attempt == self._retry_attempts - 1:
                    logger.error(
                        f"Failed to connect to Redis after {self._retry_attempts} attempts"
                    )
                    raise
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e!s}")
                await asyncio.sleep(self._retry_delay)
        raise RuntimeError("Unexpected end of connection attempts")

    async def _execute_with_retry(
        self, cmd: str, *args: object, **kwargs: object
    ) -> Any:
        for attempt in range(self._retry_attempts):
            try:
                redis = await self._get_connection()
                method = getattr(redis, cmd)
                return await method(*args, **kwargs)
            except (ConnectionError, TimeoutError):
                if attempt == self._retry_attempts - 1:
                    raise
                await asyncio.sleep(self._retry_delay)
        raise RuntimeError("Unexpected end of retry loop")

    async def get(self, key: int | str) -> Any:
        return await self._execute_with_retry("get", str(key))

    async def set(self, key: int | str, value: Any, ex: int | None = None) -> None:
        if ex is not None:
            await self._execute_with_retry("set", str(key), value, ex=ex)
        else:
            await self._execute_with_retry("set", str(key), value)

    async def remove(self, key: int | str) -> None:
        await self._execute_with_retry("delete", str(key))

    async def exists(self, key: int | str) -> bool:
        return bool(await self._execute_with_retry("exists", str(key)))

    async def keys(self, pattern: str = "*") -> list[str]:
        result = await self._execute_with_retry("keys", pattern)
        return cast(list[str], result)

    async def close(self) -> None:
        if self._redis is not None:
            try:
                await self._redis.aclose()
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e!s}")
            finally:
                self._redis = None

    async def __aenter__(self) -> Self:
        await self._get_connection()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
