from typing import Annotated, final

from fastapi import Depends

from app.core import exceptions as exc
from app.core.security import Token
from app.schemas import USER_ROLE, Payload, Role


@final
class PermissionChecker:
    """Verify user access rights based on role."""

    __slots__ = ("roles",)

    def __init__(self, *roles: USER_ROLE) -> None:
        """
        Initialize access verification.

        Args:
            roles (set[USER_ROLE]): list of allowed roles.

        """
        self.roles = set(roles) | {Role.admin}

    async def __call__(self, payload: Annotated[Payload, Depends(Token())]) -> None:
        """
        Check the user's permissions.

        Args:
            payload (Payload): payload data

        Raises:
            UserPermissionError: access is forbidden

        """
        if payload.user_role not in self.roles:
            raise exc.UserPermissionError
