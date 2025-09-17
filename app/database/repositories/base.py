from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import override

from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class RepositoryBase[Model, Create, Update, Filters](ABC):
    @abstractmethod
    async def create(self, item_create: Create) -> Model:
        """
        Create a new item.

        Args:
            item_create (Create): item data to create

        Returns:
            Model: created item's data

        """
        raise NotImplementedError

    @abstractmethod
    async def read(self, item_id: int) -> Model | None:
        """
        Read the item by id.

        Args:
            item_id (int): item id

        Returns:
            Model | None: item data

        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, item_id: int, item_update: Update) -> Model | None:
        """
        Update the item by id.

        Args:
            item_id (int): item id
            item_update (Update): item data to update

        Returns:
            Model | None: updated item data

        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, item_id: int) -> Model | None:
        """
        Delete the item by id.

        Args:
            item_id (int): item id

        Returns:
            Model | None: item data

        """
        raise NotImplementedError

    @abstractmethod
    async def read_all(self, filters: Filters) -> Sequence[Model]:
        """
        Read all items with the search filter.

        Args:
            filters (Filters): item search filter

        Returns:
            Sequence[Model]: list of items

        """
        raise NotImplementedError


class SqlAlchemyRepositoryBase[
    Model: DeclarativeBase,
    Create: BaseModel,
    Update: BaseModel,
    Filters: BaseModel,
](RepositoryBase[Model, Create, Update, Filters]):
    __slots__ = ("session",)

    model: type[Model]

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the sqlalchemy repository.

        Args:
            session (AsyncSession): instance of the database connection session

        """
        self.session = session

    @override
    async def create(self, item_create: Create) -> Model:
        new_item = self.model(**item_create.model_dump())
        self.session.add(new_item)
        await self.session.flush()
        return new_item

    @override
    async def read(self, item_id: int) -> Model | None:
        return await self.session.get(self.model, item_id)

    @override
    async def update(self, item_id: int, item_update: Update) -> Model | None:
        item = await self.read(item_id)

        if item is None:
            return None

        for key, value in item_update.model_dump().items():
            if value is not None:
                setattr(item, key, value)

        return item

    @override
    async def delete(self, item_id: int) -> Model | None:
        item = await self.read(item_id)

        if item is None:
            return None

        await self.session.delete(item)
        return item

    @override
    async def read_all(self, filters: Filters) -> Sequence[Model]:
        query = select(self.model)
        query = await self._filter_query(query, filters)
        result = await self.session.scalars(query)
        return result.all()

    @classmethod
    async def _filter_query(
        cls,
        query: Select[tuple[Model]],
        filters: Filters,
    ) -> Select[tuple[Model]]:
        """
        Filter the query by the specified search filter.

        Args:
            query (Select[tuple[Model]]): database query expression
            filters (Filters): item search filter

        Returns:
            Select[tuple[Model]]: filtered query expression

        """
        _ = filters
        return query
