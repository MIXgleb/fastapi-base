from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.api import router as router_api
from app.core.config import settings
from app.core.exception_handlers import (
    database_exception_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.loggers import setup_logger
from app.core.middlewares import LoggingMiddleware
from app.database import SqlAlchemyDB


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """
    Initialize the fastapi application lifespan.

    Args:
        _ (FastAPI): fastapi application instance

    Yields:
        AsyncGenerator[None]: open before launching, close before completion

    """
    setup_logger()
    logger.info("🚀 Application starting up...")

    logger.info("Connecting to redis...")
    redis_connection = redis.from_url(settings.redis.url, encoding=settings.redis.encoding)  # type: ignore[reportUnknownMemberType]
    logger.info("Connection to redis completed.")

    logger.info("Connecting to database...")
    db = SqlAlchemyDB()
    await db.init(str(settings.db.url))
    logger.info("Connection to database completed.")

    await FastAPILimiter.init(redis_connection)  # type: ignore[reportUnknownMemberType]

    yield

    await FastAPILimiter.close()

    logger.info("🛑 Application shutting down...")
    logger.info("Disconnecting from the database...")
    await db.close()


app = FastAPI(title="FastAPI Base Example", lifespan=lifespan)

app.include_router(router_api)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
