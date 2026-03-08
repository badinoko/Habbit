from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from .base import InDBBase


class AuthCredentials(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class AuthRegister(AuthCredentials):
    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("password must be a string")
        if len(value) < 8 or len(value) > 256:
            raise ValueError("password must be between 8 and 256 characters")
        return value


class AuthLogin(AuthCredentials):
    pass


class UserCreate(BaseModel):
    email: str
    password_hash: str | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    email: str | None = None
    password_hash: str | None = None
    is_active: bool | None = None


class AuthUser(InDBBase):
    email: str
    is_active: bool


class AuthUserWithPassword(AuthUser):
    password_hash: str | None


class OAuthAccountRead(InDBBase):
    user_id: UUID
    provider: str
    provider_user_id: str
    provider_email: str | None = None
