from abc import abstractmethod
from typing import final, override

from fastapi import Response

import app.core.exceptions as exc
from app.core.security import Password, Token
from app.schemas import Payload, TokensCreate, TokenType, UserCreate, UserInput, UserRead
from app.services.base import ServiceBase, SqlAlchemyServiceBase


class AuthServiceBase(ServiceBase):
    @abstractmethod
    async def login(self, user_input: UserInput, response: Response) -> None:
        """
        Log in to the account.

        Args:
            user_input (UserInput): user credentials
            response (Response): response to the client

        """
        raise NotImplementedError

    @abstractmethod
    async def register(self, user_input: UserInput) -> None:
        """
        Register a new user.

        Args:
            user_input (UserInput): user credentials

        """
        raise NotImplementedError


@final
class AuthService(SqlAlchemyServiceBase, AuthServiceBase):
    async def _check_user(self, user_input: UserInput) -> UserRead:
        async with self.uow as uow:
            user = await uow.users.read_by_name(user_input.username)

            if user is None:
                exc_msg = "User not found."
                raise exc.AuthorizationError(exc_msg)

            if not Password.verify(user_input.password, user.hashed_password):
                exc_msg = "Authorization failed."
                raise exc.AuthorizationError(exc_msg)

            return UserRead.model_validate(user, from_attributes=True)

    @override
    async def login(self, user_input: UserInput, response: Response) -> None:
        user = await self._check_user(user_input)

        access_token = Token.create(
            Payload(user_id=user.id, user_role=user.role, token_type=TokenType.access_token)
        )
        refresh_token = Token.create(
            Payload(user_id=user.id, user_role=user.role, token_type=TokenType.refresh_token)
        )
        tokens = TokensCreate(access_token=access_token, refresh_token=refresh_token)
        Token.set_tokens(tokens, response)

    @override
    async def register(self, user_input: UserInput) -> None:
        """
        Register a new user.

        Args:
            user_input (UserInput): user credentials

        Raises:
            UserExistsError: user already exists

        """
        async with self.uow as uow:
            user = await uow.users.read_by_name(user_input.username)

            if user is not None:
                raise exc.UserExistsError

            user_create = UserCreate(
                username=user_input.username,
                hashed_password=Password.hash(user_input.password),
                role="user",
            )

            await uow.users.create(user_create)
            await uow.commit()
