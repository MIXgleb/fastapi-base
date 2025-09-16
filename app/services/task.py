from abc import abstractmethod
from typing import Final, final, override

import app.core.exceptions as exc
from app.schemas import TaskCreate, TaskFilters, TaskInput, TaskRead, TaskUpdate
from app.services.base import ServiceBase, SqlAlchemyServiceBase

MSG_TASK_NOT_FOUND: Final[str] = "Task not found."


class TaskServiceBase(ServiceBase):
    @abstractmethod
    async def create_task(self, task_input: TaskInput, user_id: int) -> TaskRead:
        """
        Create a new task.

        Args:
            task_input (TaskInput): new task data
            user_id (int): task user id

        Returns:
            TaskRead: new task data

        """
        raise NotImplementedError

    @abstractmethod
    async def get_all_tasks(self, filters: TaskFilters, user_id: int) -> list[TaskRead]:
        """
        Get the user's filtered tasks.

        Args:
            filters (TaskFilters): task search filter
            user_id (int): relation user id

        Returns:
            list[TaskRead]: list of tasks

        """
        raise NotImplementedError

    @abstractmethod
    async def get_task(self, task_id: int) -> TaskRead:
        """
        Get the task by id.

        Args:
            task_id (int): task id

        Returns:
            TaskRead: task data

        """
        raise NotImplementedError

    @abstractmethod
    async def update_task(self, task_update: TaskUpdate, task_id: int) -> TaskRead:
        """
        Update the task by id.

        Args:
            task_update (TaskUpdate): task data to update
            task_id (int): task id

        Returns:
            TaskRead: updated task data

        """
        raise NotImplementedError

    @abstractmethod
    async def delete_task(self, task_id: int) -> TaskRead:
        """
        Delete the task by id.

        Args:
            task_id (int): task id

        Returns:
            TaskRead: task data

        """
        raise NotImplementedError


@final
class TaskService(SqlAlchemyServiceBase, TaskServiceBase):
    @override
    async def create_task(self, task_input: TaskInput, user_id: int) -> TaskRead:
        task_create = TaskCreate(**task_input.model_dump(), user_id=user_id)

        async with self.uow as uow:
            task = await uow.tasks.create(task_create)
            await uow.commit()
            return TaskRead.model_validate(task, from_attributes=True)

    @override
    async def get_all_tasks(self, filters: TaskFilters, user_id: int) -> list[TaskRead]:
        async with self.uow as uow:
            tasks = await uow.tasks.read_all(filters, user_id)
            return [TaskRead.model_validate(task, from_attributes=True) for task in tasks]

    @override
    async def get_task(self, task_id: int) -> TaskRead:
        """
        Get the task by id.

        Args:
            task_id (int): task id

        Raises:
            ResourceNotFoundError: task not found

        Returns:
            TaskRead: task data

        """
        async with self.uow as uow:
            task = await uow.tasks.read(task_id)

            if task is None:
                raise exc.ResourceNotFoundError(MSG_TASK_NOT_FOUND)

            return TaskRead.model_validate(task, from_attributes=True)

    @override
    async def update_task(self, task_update: TaskUpdate, task_id: int) -> TaskRead:
        """
        Update the task by id.

        Args:
            task_update (TaskUpdate): task data to update
            task_id (int): task id

        Raises:
            ResourceNotFoundError: task not found

        Returns:
            TaskRead: updated task data

        """
        async with self.uow as uow:
            task = await uow.tasks.update(task_id, task_update)

            if task is None:
                raise exc.ResourceNotFoundError(MSG_TASK_NOT_FOUND)

            await uow.commit()
            return TaskRead.model_validate(task, from_attributes=True)

    @override
    async def delete_task(self, task_id: int) -> TaskRead:
        """
        Delete the task by id.

        Args:
            task_id (int): task id

        Raises:
            ResourceNotFoundError: task not found

        Returns:
            TaskRead: task data

        """
        async with self.uow as uow:
            task = await uow.tasks.delete(task_id)

            if task is None:
                raise exc.ResourceNotFoundError(MSG_TASK_NOT_FOUND)

            await uow.commit()
            return TaskRead.model_validate(task, from_attributes=True)
