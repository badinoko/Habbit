from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.schemas.auth import AuthRegister


def test_auth_register_normalizes_email() -> None:
    payload = AuthRegister(email="  USER@Example.com ", password="strong-pass-123")
    assert payload.email == "user@example.com"


def test_auth_register_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError, match="value is not a valid email address"):
        AuthRegister(email="not-an-email", password="strong-pass-123")


def test_auth_register_rejects_short_password() -> None:
    with pytest.raises(ValueError, match="password must be between 8 and 256 characters"):
        AuthRegister(email="user@example.com", password="short")
