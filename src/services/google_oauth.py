import json
from typing import Any
from urllib.parse import urlencode

import httpx

from src.exceptions import GoogleOauthError
from src.schemas.google import GoogleOauthToken, GoogleOauthUser


class GoogleOauth:
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: tuple[str, ...] | None = None,
        timeout: float = 10.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or (
            "openid",
            "email",
            "profile",
        )
        self.timeout = timeout
        self._http_client = http_client

    def get_authorization_url(
        self,
        state: str,
        *,
        access_type: str = "offline",
        prompt: str = "consent",
        login_hint: str | None = None,
    ) -> str:
        query_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": access_type,
            "prompt": prompt,
            "include_granted_scopes": "true",
        }
        if login_hint:
            query_params["login_hint"] = login_hint
        return f"{self.AUTHORIZE_URL}?{urlencode(query_params)}"

    async def exchange_code_for_token(self, code: str) -> GoogleOauthToken:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        response = await self._post_json(self.TOKEN_URL, payload)
        try:
            return GoogleOauthToken.model_validate(response)
        except ValueError as exc:
            raise GoogleOauthError("Google token response was invalid") from exc

    async def get_user_info(self, access_token: str) -> GoogleOauthUser:
        response = await self._get_json(
            self.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        provider_user_id = response.get("sub") or response.get("id")
        email = response.get("email")
        email_verified = response.get("email_verified")
        if not isinstance(provider_user_id, str) or not provider_user_id:
            raise GoogleOauthError("Google userinfo response did not include user id")
        if not isinstance(email, str) or not email:
            raise GoogleOauthError("Google userinfo response did not include email")
        if not isinstance(email_verified, bool):
            raise GoogleOauthError(
                "Google userinfo response did not include a boolean email_verified"
            )

        try:
            return GoogleOauthUser.model_validate(
                {
                    "provider_user_id": provider_user_id,
                    "email": email,
                    "email_verified": email_verified,
                    "name": self._optional_str(response.get("name")),
                    "given_name": self._optional_str(response.get("given_name")),
                    "family_name": self._optional_str(response.get("family_name")),
                    "picture": self._optional_str(response.get("picture")),
                }
            )
        except ValueError as exc:
            raise GoogleOauthError("Google userinfo response was invalid") from exc

    async def authenticate(self, code: str) -> GoogleOauthUser:
        token_payload = await self.exchange_code_for_token(code)
        return await self.get_user_info(token_payload.access_token)

    async def _post_json(
        self,
        url: str,
        payload: dict[str, str],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        request_headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if headers:
            request_headers.update(headers)
        return await self._request_json(
            "POST",
            url,
            content=urlencode(payload).encode("utf-8"),
            headers=request_headers,
        )

    async def _get_json(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        request_headers = {"Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        return await self._request_json("GET", url, headers=request_headers)

    async def _request_json(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        content: bytes | None = None,
    ) -> dict[str, Any]:
        try:
            response = await self._send_request(
                method=method,
                url=url,
                headers=headers,
                content=content,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GoogleOauthError(
                f"Google OAuth request failed with status "
                f"{exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:
            raise GoogleOauthError("Google OAuth request failed") from exc

        raw_body = response.text
        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise GoogleOauthError("Google OAuth response was not valid JSON") from exc

        if not isinstance(parsed, dict):
            raise GoogleOauthError("Google OAuth response was not a JSON object")
        return parsed

    async def _send_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        content: bytes | None = None,
    ) -> httpx.Response:
        if self._http_client is not None:
            return await self._http_client.request(
                method,
                url,
                headers=headers,
                content=content,
                timeout=self.timeout,
            )

        async with httpx.AsyncClient() as client:
            return await client.request(
                method,
                url,
                headers=headers,
                content=content,
                timeout=self.timeout,
            )

    @staticmethod
    def _optional_str(value: object) -> str | None:
        return value if isinstance(value, str) and value else None
