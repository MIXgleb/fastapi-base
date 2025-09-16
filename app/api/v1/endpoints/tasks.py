from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from app.api.v1.deps import PermissionChecker, TaskOwnershipChecker
from app.api.v1.schemas import MessageDeleteTaskReturn, MessageUpdateTaskReturn
from app.core.config import settings
from app.core.security import Token
from app.schemas import Payload, Role, TaskFilters, TaskInput, TaskRead, TaskUpdate
from app.services import SqlAlchemyServiceHelper, TaskService, TaskServiceBase

router = APIRouter(prefix=settings.api.v1.tasks, tags=["Tasks"])
task_service_helper = SqlAlchemyServiceHelper(TaskService)


@router.post(
    "/task",
    dependencies=[Depends(PermissionChecker(Role.admin, Role.user))],
)
async def create_task(
    task_service: Annotated[TaskServiceBase, Depends(task_service_helper.service_getter)],
    payload: Annotated[Payload, Depends(Token())],
    task_input: Annotated[TaskInput, Body()],
) -> TaskRead:
    """
    Create a new task.

    Args:
        task_service (TaskServiceBase): task service
        payload (Payload): payload data
        task_input (TaskInput): new task data

    Returns:
        TaskRead: task data

    """
    return await task_service.create_task(task_input, payload.user_id)


@router.get(
    "/all",
    dependencies=[Depends(PermissionChecker(Role.admin, Role.user))],
)
async def get_all_tasks(
    task_service: Annotated[TaskServiceBase, Depends(task_service_helper.service_getter)],
    payload: Annotated[Payload, Depends(Token())],
    filters: Annotated[TaskFilters, Query()],
) -> list[TaskRead]:
    """
    Get all the user's tasks.

    Args:
        task_service (TaskServiceBase): task service
        payload (Payload): payload data
        filters (TaskFilters): task search filter

    Returns:
        list[TaskRead]: data of tasks

    """
    return await task_service.get_all_tasks(filters, payload.user_id)


@router.get(
    "/{task_id}",
    dependencies=[Depends(TaskOwnershipChecker(task_service_helper))],
)
async def get_task(
    task_service: Annotated[TaskServiceBase, Depends(task_service_helper.service_getter)],
    task_id: Annotated[int, Path()],
) -> TaskRead:
    """
    Get the task by id.

    Args:
        task_service (TaskServiceBase): task service
        task_id (int): task id

    Returns:
        TaskRead: task data

    """
    return await task_service.get_task(task_id)


@router.put(
    "/{task_id}",
    dependencies=[
        Depends(PermissionChecker(Role.admin, Role.user)),
        Depends(TaskOwnershipChecker(task_service_helper)),
    ],
)
async def update_task(
    task_service: Annotated[TaskServiceBase, Depends(task_service_helper.service_getter)],
    task_id: Annotated[int, Path()],
    task_update: Annotated[TaskUpdate, Body()],
) -> MessageUpdateTaskReturn:
    """
    Update the task by id.

    Args:
        task_service (TaskServiceBase): task service
        task_id (int): task id
        task_update (TaskUpdate): task data to update

    Returns:
        MessageUpdateTaskReturn: status message

    """
    task = await task_service.update_task(task_update, task_id)
    return MessageUpdateTaskReturn(task=task)


@router.delete(
    "/{task_id}",
    dependencies=[
        Depends(PermissionChecker(Role.admin, Role.user)),
        Depends(TaskOwnershipChecker(task_service_helper)),
    ],
)
async def delete_task(
    task_service: Annotated[TaskServiceBase, Depends(task_service_helper.service_getter)],
    task_id: Annotated[int, Path()],
) -> MessageDeleteTaskReturn:
    """
    Delete the task by id.

    Args:
        task_service (TaskServiceBase): task service
        task_id (int): task id

    Returns:
        MessageDeleteTaskReturn: status message

    """
    task = await task_service.delete_task(task_id)
    return MessageDeleteTaskReturn(task=task)
