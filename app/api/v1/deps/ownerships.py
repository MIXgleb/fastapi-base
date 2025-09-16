from typing import Annotated, final

from fastapi import Depends, Path, Request

from app.core import exceptions as exc
from app.core.security import Token
from app.schemas import Payload, Role
from app.services import SqlAlchemyServiceHelper, TaskService


@final
class UserOwnershipChecker:
    """Verifying the user's ownership of a resource."""

    async def __call__(
        self,
        user_id: Annotated[int, Path()],
        payload: Annotated[Payload, Depends(Token())],
        request: Request,
    ) -> None:
        """
        Check the user's ownership rights.

        Args:
            user_id (int): user id
            payload (Payload): payload data
            request (Request): request from the client

        Raises:
            WrondMethodError: method not allowed
            ResourceOwnershipError: access is forbidden

        """
        method = request.method
        is_admin = payload.user_role == Role.admin

        if method == "POST":
            raise exc.WrondMethodError

        if method in {"GET", "PUT", "DELETE"} and (is_admin or user_id == payload.user_id):
            return

        raise exc.ResourceOwnershipError


@final
class TaskOwnershipChecker:
    """Verifying the user's ownership of a task."""

    __slots__ = ("service_helper",)

    def __init__(self, service_helper: SqlAlchemyServiceHelper[TaskService]) -> None:
        """
        Initialize resource ownership verification.

        Args:
            service_helper (SqlAlchemyServiceHelper): task service helper

        """
        self.service_helper = service_helper

    async def __call__(
        self,
        payload: Annotated[Payload, Depends(Token())],
        task_id: Annotated[int, Path()],
        request: Request,
    ) -> None:
        """
        Check the user's ownership rights.

        Args:
            payload (Payload): payload data
            task_id (int): task id
            request (Request): request from the client

        Raises:
            WrondMethodError: method not allowed
            ResourceOwnershipError: access is forbidden

        """
        method = request.method
        is_admin = payload.user_role == Role.admin
        task = await self.service_helper.service.get_task(task_id)

        if method == "POST":
            raise exc.WrondMethodError

        if method == "GET" and (is_admin or task.user_id == payload.user_id or task.is_public):
            return

        if method in {"PUT", "DELETE"} and (is_admin or task.user_id == payload.user_id):
            return

        raise exc.ResourceOwnershipError
