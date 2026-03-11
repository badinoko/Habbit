from pydantic import BaseModel, EmailStr


class GoogleOauthToken(BaseModel):
    access_token: str
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None
    token_type: str | None = None
    id_token: str | None = None


class GoogleOauthUser(BaseModel):
    provider_user_id: str
    email: EmailStr
    email_verified: bool
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
