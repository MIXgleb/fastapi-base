from collections.abc import Sequence
from typing import final, override

from sqlalchemy import Select, select

from app.core.exceptions import QueryValueError
from app.database.models import Task
from app.database.repositories.base import RepositoryBase, SqlAlchemyRepositoryBase
from app.schemas import TaskCreate, TaskFilters, TaskUpdate


class TaskRepositoryBase(RepositoryBase[Task, TaskCreate, TaskUpdate, TaskFilters]):
    @override
    async def read_all(self, filters: TaskFilters, relation_id: int = -1) -> Sequence[Task]:
        """
        Read all tasks with the search filter.

        Args:
            filters (TaskFilters): task search filter
            relation_id (int, optional): relationship user id. Defaults to -1.

        Raises:
            TypeError: missing 'relation_id' argument

        Returns:
            Sequence[Task]: list of tasks

        """
        raise NotImplementedError


@final
class TaskRepository(
    SqlAlchemyRepositoryBase[Task, TaskCreate, TaskUpdate, TaskFilters],
    TaskRepositoryBase,
):
    model = Task

    @override
    async def read_all(self, filters: TaskFilters, relation_id: int = -1) -> Sequence[Task]:
        if relation_id == -1:
            msg_err = "read_all() missing 1 required positional argument: 'relation_id'"
            raise TypeError(msg_err)

        query = select(self.model)
        query = await self._filter_query(query, filters, relation_id)
        result = await self.session.scalars(query)
        return result.all()

    @classmethod
    @override
    async def _filter_query(
        cls,
        query: Select[tuple[Task]],
        filters: TaskFilters,
        relation_id: int = -1,
    ) -> Select[tuple[Task]]:
        query = query.where(cls.model.user_id == relation_id)

        if (title := filters.title_contains) is not None:
            query = query.where(cls.model.title.ilike(f"%{title}%"))
        if (is_public := filters.public) is not None:
            query = query.where(cls.model.is_public == is_public)
        if (is_completed := filters.completed) is not None:
            query = query.where(cls.model.is_completed == is_completed)
        if hasattr(cls.model, filters.sort_by.removeprefix("-")):
            sort_attr = getattr(cls.model, filters.sort_by.removeprefix("-"))
        else:
            raise QueryValueError(filters.sort_by.removeprefix("-"), "sort-by")

        sort_by = sort_attr.desc() if filters.sort_by.startswith("-") else sort_attr.asc()
        return query.order_by(sort_by).limit(filters.limit).offset(filters.offset)
