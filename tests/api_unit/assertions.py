from __future__ import annotations

from httpx import Response


def assert_content_type(response: Response, prefix: str) -> None:
    assert response.headers["content-type"].startswith(prefix)


def assert_html_response(response: Response, *, status_code: int) -> None:
    assert response.status_code == status_code
    assert_content_type(response, "text/html")


def assert_json_response(response: Response, *, status_code: int) -> None:
    assert response.status_code == status_code
    assert_content_type(response, "application/json")


def assert_redirect(
    response: Response,
    *,
    location: str,
    status_code: int = 303,
) -> None:
    assert response.status_code == status_code
    assert response.headers["location"] == location


def assert_json_detail(
    response: Response,
    *,
    status_code: int,
    detail: str,
) -> None:
    assert_json_response(response, status_code=status_code)
    assert response.json()["detail"] == detail
