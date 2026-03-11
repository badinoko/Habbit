import httpx
import pytest

from src.exceptions import GoogleOauthError
from src.services.google_oauth import GoogleOauth


@pytest.mark.asyncio
async def test_exchange_code_for_token_uses_async_http_client() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "access_token": "google-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = GoogleOauth(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://localhost/auth/google/callback",
            http_client=http_client,
        )

        token = await client.exchange_code_for_token("oauth-code")

    assert token.access_token == "google-access-token"
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert str(captured_request.url) == GoogleOauth.TOKEN_URL
    assert (
        captured_request.headers["content-type"]
        == "application/x-www-form-urlencoded"
    )
    assert captured_request.content == (
        b"client_id=client-id&client_secret=client-secret&code=oauth-code"
        b"&grant_type=authorization_code"
        b"&redirect_uri=http%3A%2F%2Flocalhost%2Fauth%2Fgoogle%2Fcallback"
    )


@pytest.mark.asyncio
async def test_get_user_info_uses_authorization_header() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={
                "sub": "google-user-1",
                "email": "oauth@example.com",
                "email_verified": True,
                "name": "OAuth User",
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = GoogleOauth(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://localhost/auth/google/callback",
            http_client=http_client,
        )

        user = await client.get_user_info("access-token")

    assert user.provider_user_id == "google-user-1"
    assert str(user.email) == "oauth@example.com"
    assert captured_request is not None
    assert captured_request.method == "GET"
    assert str(captured_request.url) == GoogleOauth.USERINFO_URL
    assert captured_request.headers["authorization"] == "Bearer access-token"


@pytest.mark.asyncio
async def test_get_user_info_rejects_non_boolean_email_verified() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "sub": "google-user-1",
                "email": "oauth@example.com",
                "email_verified": "false",
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = GoogleOauth(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://localhost/auth/google/callback",
            http_client=http_client,
        )

        with pytest.raises(
            GoogleOauthError,
            match="Google userinfo response did not include a boolean email_verified",
        ):
            await client.get_user_info("access-token")


@pytest.mark.asyncio
async def test_exchange_code_for_token_converts_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="invalid_grant")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = GoogleOauth(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://localhost/auth/google/callback",
            http_client=http_client,
        )

        with pytest.raises(GoogleOauthError, match="status 401: invalid_grant"):
            await client.exchange_code_for_token("oauth-code")


@pytest.mark.asyncio
async def test_exchange_code_for_token_rejects_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        client = GoogleOauth(
            client_id="client-id",
            client_secret="client-secret",
            redirect_uri="http://localhost/auth/google/callback",
            http_client=http_client,
        )

        with pytest.raises(
            GoogleOauthError, match="Google OAuth response was not valid JSON"
        ):
            await client.exchange_code_for_token("oauth-code")
