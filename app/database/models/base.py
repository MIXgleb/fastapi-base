from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """
        Get the tablename from the classname.

        Returns:
            str: tablename

        """
        return f"{cls.__name__.lower()}s"
