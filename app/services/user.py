from abc import abstractmethod
from typing import Final, final, override

import app.core.exceptions as exc
from app.schemas import UserFilters, UserRead
from app.services.base import ServiceBase, SqlAlchemyServiceBase

MSG_USER_NOT_FOUND: Final[str] = "User not found."


class UserServiceBase(ServiceBase):
    @abstractmethod
    async def get_all_users(self, filters: UserFilters) -> list[UserRead]:
        """
        Get the filtered users.

        Args:
            filters (UserFilters): user search filter

        Returns:
            list[UserRead]: list of users

        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: int) -> UserRead:
        """
        Get the user by id.

        Args:
            user_id (int): user id

        Returns:
            UserRead: user data

        """
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: int) -> UserRead:
        """
        Delete the user by id.

        Args:
            user_id (int): user id

        Returns:
            UserRead: user data

        """
        raise NotImplementedError


@final
class UserService(SqlAlchemyServiceBase, UserServiceBase):
    @override
    async def get_all_users(self, filters: UserFilters) -> list[UserRead]:
        async with self.uow as uow:
            users = await uow.users.read_all(filters)
            return [UserRead.model_validate(user, from_attributes=True) for user in users]

    @override
    async def get_user(self, user_id: int) -> UserRead:
        """
        Get the user by id.

        Args:
            user_id (int): user id

        Raises:
            ResourceNotFoundError: user not found

        Returns:
            UserRead: user data

        """
        async with self.uow as uow:
            user = await uow.users.read(user_id)

            if user is None:
                raise exc.ResourceNotFoundError(MSG_USER_NOT_FOUND)

            return UserRead.model_validate(user, from_attributes=True)

    @override
    async def delete_user(self, user_id: int) -> UserRead:
        """
        Delete the user by id.

        Args:
            user_id (int): user id

        Raises:
            ResourceNotFoundError: user not found

        Returns:
            UserRead: user data

        """
        async with self.uow as uow:
            user = await uow.users.delete(user_id)

            if user is None:
                raise exc.ResourceNotFoundError(MSG_USER_NOT_FOUND)

            await uow.commit()
            return UserRead.model_validate(user, from_attributes=True)
