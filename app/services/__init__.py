__all__ = (
    "AuthService",
    "AuthServiceBase",
    "TaskService",
    "TaskServiceBase",
    "UserService",
    "UserServiceBase",
)

from abc import ABC, abstractmethod
from typing import Any, final, override

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.database import DbBase, DbUOW, SqlAlchemyDB, SqlAlchemyUOW, UOWBase
from app.services.auth import AuthService, AuthServiceBase
from app.services.base import DbServiceBase, ServiceBase, SqlAlchemyServiceBase
from app.services.task import TaskService, TaskServiceBase
from app.services.user import UserService, UserServiceBase


class ServiceHelperBase[UOWType: UOWBase](ABC):
    __slots__ = ("type_service",)

    type_uow: type[UOWType]

    @abstractmethod
    async def service_getter(self) -> ServiceBase:
        """
        Get an instance of the service.

        Returns:
            ServiceBase: service instance

        """
        raise NotImplementedError

    @property
    @abstractmethod
    def service(self) -> ServiceBase:
        """
        Service.

        Returns:
            ServiceBase: service instance

        """
        raise NotImplementedError


class DbServiceHelperBase[
    Engine,
    Session,
    SessionFactory,
    Service: DbServiceBase[Any, Any, Any],
](ServiceHelperBase[DbUOW[Engine, Session, SessionFactory]]):
    __slots__ = ("db",)

    type_uow: type[DbUOW[Engine, Session, SessionFactory]]
    type_db: type[DbBase[Engine, Session, SessionFactory]]

    def __init__(self, type_service: type[Service]) -> None:
        """
        Initialize the database service helper.

        Args:
            type_service (type[DatabaseServiceBase]): type of service database

        """
        self.type_service = type_service
        self.db = self.type_db()

    @override
    async def service_getter(self) -> Service:
        return self.type_service(self.type_uow, self.db)

    @property
    @override
    def service(self) -> Service:
        return self.type_service(self.type_uow, self.db)


@final
class SqlAlchemyServiceHelper[Service: SqlAlchemyServiceBase](
    DbServiceHelperBase[
        AsyncEngine,
        AsyncSession,
        async_sessionmaker[AsyncSession],
        Service,
    ]
):
    type_uow = SqlAlchemyUOW
    type_db = SqlAlchemyDB
