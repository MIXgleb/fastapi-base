from abc import abstractmethod
from typing import final, override

from pydantic import BaseModel
from sqlalchemy import Select, select

from app.core.exceptions import QueryValueError
from app.database.models import User
from app.database.repositories.base import RepositoryBase, SqlAlchemyRepositoryBase
from app.schemas import UserCreate, UserFilters


class UserRepositoryBase(RepositoryBase[User, UserCreate, BaseModel, UserFilters]):
    @abstractmethod
    async def read_by_name(self, username: str) -> User | None:
        """
        Read the user by username.

        Args:
            username (str): user name

        Returns:
            User: user data

        """
        raise NotImplementedError


@final
class UserRepository(
    SqlAlchemyRepositoryBase[User, UserCreate, BaseModel, UserFilters],
    UserRepositoryBase,
):
    model = User

    @override
    async def read_by_name(self, username: str) -> User | None:
        query = select(self.model).where(self.model.username == username)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    @override
    async def update(self, item_id: int, item_update: BaseModel) -> User | None:
        """Not implemented."""
        raise NotImplementedError

    @classmethod
    @override
    async def _filter_query(
        cls,
        query: Select[tuple[User]],
        filters: UserFilters,
    ) -> Select[tuple[User]]:
        if (username := filters.username_contains) is not None:
            query = query.where(cls.model.username.ilike(f"%{username}%"))
        if (roles := filters.role) is not None:
            query = query.where(cls.model.role.in_(roles))
        if hasattr(cls.model, filters.sort_by.removeprefix("-")):
            sort_attr = getattr(cls.model, filters.sort_by.removeprefix("-"))
        else:
            raise QueryValueError(filters.sort_by.removeprefix("-"), "sort-by")

        sort_by = sort_attr.desc() if filters.sort_by.startswith("-") else sort_attr.asc()
        return query.order_by(sort_by).limit(filters.limit).offset(filters.offset)
