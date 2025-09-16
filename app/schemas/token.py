from datetime import UTC, datetime
from typing import Literal, Self, assert_never

from pydantic import BaseModel, computed_field, model_validator

from app.core.config import settings
from app.schemas.user import USER_ROLE

type TOKEN = Literal["access_token", "refresh_token", "guest_token"]


class TokenType:
    access_token: TOKEN = "access_token"  # noqa: S105
    refresh_token: TOKEN = "refresh_token"  # noqa: S105
    guest_token: TOKEN = "guest_token"  # noqa: S105


class TokensRead(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    guest_token: str | None = None


class TokensCreate(BaseModel):
    access_token: str
    refresh_token: str


class Payload(BaseModel):
    user_id: int
    user_role: USER_ROLE
    token_type: TOKEN

    @computed_field
    @property
    def exp(self) -> datetime:  # noqa: D102
        match self.token_type:
            case "access_token":
                return datetime.now(UTC) + settings.token.access_token_timedelta
            case "refresh_token":
                return datetime.now(UTC) + settings.token.refresh_token_timedelta
            case "guest_token":
                return datetime.now(UTC) + settings.token.guest_token_timedelta
            case _:
                assert_never(self.token_type)

    @model_validator(mode="after")
    def check_user_id(self) -> Self:  # noqa: D102
        if self.user_id != 0 or self.token_type == TokenType.guest_token:
            return self

        raise ValueError
