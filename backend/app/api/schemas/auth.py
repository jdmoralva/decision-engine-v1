from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: str
    username: str
    display_name: str | None
    roles: list[str]
    authorization_mode: str = Field(
        default="request_time",
        description="Protected endpoints resolve permissions from persisted assignments on each request.",
    )
