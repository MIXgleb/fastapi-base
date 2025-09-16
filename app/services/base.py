from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.database import DbBase, DbUOW, UOWBase


class ServiceBase:
    __slots__ = ("uow",)

    def __init__(self, type_uow: type[UOWBase]) -> None:
        """
        Initialize the service.

        Args:
            type_uow (type[UOWBase]): unit-of-work interface

        """
        self.uow = type_uow()


class DbServiceBase[Engine, Session, SessionFactory](ServiceBase):
    def __init__(
        self,
        type_uow: type[DbUOW[Engine, Session, SessionFactory]],
        db: DbBase[Engine, Session, SessionFactory],
    ) -> None:
        """
        Initialize the database service.

        Args:
            type_uow (type[DbUOW]): database unit-of-work interface
            db (DbBase): database helper instance

        """
        self.uow = type_uow(db)


class SqlAlchemyServiceBase(
    DbServiceBase[AsyncEngine, AsyncSession, async_sessionmaker[AsyncSession]]
): ...
