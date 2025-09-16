from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Self, final, override

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import app.core.exceptions as exc
from app.core.config import settings


class DbBase[Engine, Session, SessionFactory](ABC):
    __slots__ = ("_engine", "_session_factory")

    _instance: Self | None = None

    @final
    def __new__(cls) -> Self:
        """
        Singleton.

        Returns:
            Self: only instance of the class

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the database helper."""
        self._engine: Engine | None = None
        self._session_factory: SessionFactory | None = None

    @abstractmethod
    async def init(self, url: str) -> None:
        """
        Initialize the db session.

        Args:
            url (str): connection url

        """
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close the db session."""
        raise NotImplementedError

    @abstractmethod
    async def session_getter(self) -> AsyncGenerator[Session]:
        """
        Get the created db session.

        Yields:
            AsyncGenerator[Session]: instance of db session

        """
        raise NotImplementedError
        yield

    @final
    @property
    def session_factory(self) -> SessionFactory:
        """
        Get the session factory.

        Raises:
            DatabaseSessionError: session is not initialized

        Returns:
            SessionFactory: session factory

        """
        if self._session_factory is None:
            raise exc.DatabaseSessionError

        return self._session_factory


@final
class SqlAlchemyDB(DbBase[AsyncEngine, AsyncSession, async_sessionmaker[AsyncSession]]):
    @override
    async def init(self, url: str) -> None:
        self._engine = create_async_engine(
            url=url,
            echo=settings.db.echo,
            echo_pool=settings.db.echo_pool,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @override
    async def close(self) -> None:
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    @override
    async def session_getter(self) -> AsyncGenerator[AsyncSession]:
        """
        Get the created db session.

        Yields:
            AsyncGenerator[AsyncSession]: instance of db session

        Raises:
            DatabaseSessionError: session is not initialized

        """
        if self._session_factory is None:
            raise exc.DatabaseSessionError

        async with self._session_factory() as session:
            yield session
