from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.v1.deps import PermissionChecker, UserOwnershipChecker
from app.api.v1.schemas import MessageDeleteUserReturn
from app.core.config import settings
from app.core.security import Token
from app.schemas import Payload, Role, UserFilters, UserRead
from app.services import SqlAlchemyServiceHelper, UserService, UserServiceBase

router = APIRouter(prefix=settings.api.v1.users, tags=["Users"])
user_service_helper = SqlAlchemyServiceHelper(UserService)


@router.get("/me")
async def get_me(
    user_service: Annotated[UserServiceBase, Depends(user_service_helper.service_getter)],
    payload: Annotated[Payload, Depends(Token())],
) -> UserRead:
    """
    Get my user's information.

    Args:
        user_service (UserServiceBase): user service
        payload (Payload): payload data

    Returns:
        UserRead: user data

    """
    if payload.user_id == 0:
        return UserRead(username="guest", id=payload.user_id, role=payload.user_role)
    return await user_service.get_user(payload.user_id)


@router.get(
    "/all",
    dependencies=[Depends(PermissionChecker(Role.admin))],
)
async def get_all_users(
    user_service: Annotated[UserServiceBase, Depends(user_service_helper.service_getter)],
    filters: Annotated[UserFilters, Query()],
) -> list[UserRead]:
    """
    Get all users.

    Args:
        user_service (UserServiceBase): user service
        filters (UserFilters): user search filter

    Returns:
        list[UserRead]: data of users

    """
    return await user_service.get_all_users(filters)


@router.get(
    "/{user_id}",
    dependencies=[
        Depends(PermissionChecker(Role.admin, Role.user)),
        Depends(UserOwnershipChecker()),
    ],
)
async def get_user(
    user_service: Annotated[UserServiceBase, Depends(user_service_helper.service_getter)],
    user_id: Annotated[int, Path()],
) -> UserRead:
    """
    Get user's information by id.

    Args:
        user_service (UserServiceBase): user service
        user_id (int): user id

    Returns:
        UserRead: user data

    """
    return await user_service.get_user(user_id)


@router.delete(
    "/{user_id}",
    dependencies=[
        Depends(PermissionChecker(Role.admin, Role.user)),
        Depends(UserOwnershipChecker()),
    ],
)
async def delete_user(
    user_service: Annotated[UserServiceBase, Depends(user_service_helper.service_getter)],
    user_id: Annotated[int, Path()],
) -> MessageDeleteUserReturn:
    """
    Delete user by id.

    Args:
        user_service (UserServiceBase): user service
        user_id (int): user id

    Returns:
        MessageDeleteUserReturn: status message

    """
    user = await user_service.delete_user(user_id)
    return MessageDeleteUserReturn(user=user)
