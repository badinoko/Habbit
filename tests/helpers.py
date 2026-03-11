from __future__ import annotations

import re

from httpx import AsyncClient

_META_CSRF_RE = re.compile(r'<meta name="csrf-token" content="([^"]+)"')
_INPUT_CSRF_RE = re.compile(r'name="csrf_token" value="([^"]+)"')


def extract_csrf_token(html: str) -> str:
    for pattern in (_META_CSRF_RE, _INPUT_CSRF_RE):
        match = pattern.search(html)
        if match is not None:
            return match.group(1)
    raise AssertionError("CSRF token not found in HTML response")


async def fetch_csrf_token(client: AsyncClient, path: str = "/") -> str:
    response = await client.get(path)
    assert response.status_code == 200
    return extract_csrf_token(response.text)


async def with_csrf_form(
    client: AsyncClient,
    data: dict[str, object] | None = None,
    *,
    path: str = "/",
) -> dict[str, object]:
    payload = dict(data or {})
    payload["csrf_token"] = await fetch_csrf_token(client, path)
    return payload


async def with_csrf_headers(
    client: AsyncClient,
    headers: dict[str, str] | None = None,
    *,
    path: str = "/",
) -> dict[str, str]:
    request_headers = dict(headers or {})
    request_headers["X-CSRFToken"] = await fetch_csrf_token(client, path)
    return request_headers
