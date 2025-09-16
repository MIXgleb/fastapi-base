from datetime import timedelta
from pathlib import Path
from typing import Self

from loguru import logger
from pydantic import BaseModel, Field, PostgresDsn, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class _LoggerConfig(BaseModel):
    enabled: bool = True
    level: str = "INFO"
    path: str = "logs/{time:YYYY-MM-DD}/log.log"
    rotation: str = "00:00"
    retention: str = "60 days"

    @field_validator("level")
    @classmethod
    def validate_level(cls, level: str) -> str:
        valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

        if level.upper() not in valid_levels:
            exc_msg = f"Invalid log level. Must be one of: {valid_levels}"
            raise ValueError(exc_msg)

        return level.upper()


class _LoggingConfig(BaseModel):
    stream: _LoggerConfig
    common_file: _LoggerConfig
    error_file: _LoggerConfig
    json_file: _LoggerConfig

    path_folder: Path = Field(
        default=Path("logs").resolve(),
        description="The path to the logs folder.",
    )

    @model_validator(mode="after")
    def create_log_folder(self) -> Self:
        self.path_folder.mkdir(exist_ok=True, parents=True)
        return self

    @model_validator(mode="after")
    def remove_existing_logger(self) -> Self:
        logger.remove()
        return self


class _TokenConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_timedelta: timedelta = timedelta(minutes=1)
    refresh_token_timedelta: timedelta = timedelta(minutes=5)
    guest_token_timedelta: timedelta = timedelta(days=1)

    @computed_field
    @property
    def access_token_expiration(self) -> int:
        return int(self.access_token_timedelta.total_seconds())

    @computed_field
    @property
    def refresh_token_expiration(self) -> int:
        return int(self.refresh_token_timedelta.total_seconds())

    @computed_field
    @property
    def guest_token_expiration(self) -> int:
        return int(self.guest_token_timedelta.total_seconds())


class _RedisConfig(BaseModel):
    url: str
    encoding: str = "utf8"


class _RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class _ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    tasks: str = "/tasks"
    health: str = "/health"


class _ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: _ApiV1Prefix = _ApiV1Prefix()


class _DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )

    token: _TokenConfig
    db: _DatabaseConfig
    redis: _RedisConfig
    logging: _LoggingConfig

    run: _RunConfig = _RunConfig()
    api: _ApiPrefix = _ApiPrefix()


settings = _Settings()  # type: ignore[reportCallIssue]
