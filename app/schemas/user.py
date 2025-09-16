from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type USER_ROLE = Literal["guest", "user", "admin"]


class Role:
    guest: USER_ROLE = "guest"
    user: USER_ROLE = "user"
    admin: USER_ROLE = "admin"


class UserBase(BaseModel):
    username: str


class UserInput(UserBase):
    password: str


class UserCreate(UserBase):
    hashed_password: str
    role: USER_ROLE


class UserRead(UserBase):
    id: int
    role: USER_ROLE


class UserFilters(BaseModel):
    limit: int = Field(default=10, le=100, ge=1)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="id", validation_alias="sort-by")
    username_contains: str | None = Field(default=None, validation_alias="username-contains")
    role: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)
