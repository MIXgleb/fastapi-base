from typing import Annotated

import jwt
from fastapi import Cookie, Response
from passlib.context import CryptContext

import app.core.exceptions as exc
from app.core.config import settings
from app.schemas import Payload, Role, TokensCreate, TokensRead, TokenType


class Token:
    async def __call__(
        self,
        tokens: Annotated[TokensRead, Cookie()],
        response: Response,
    ) -> Payload:
        """
        Decode the access token.

        Check the expiration of the access token.

        Update the access token.

        Args:
            tokens (TokensRead): client's tokens
            response (Response): response to the client

        Returns:
            Payload: payload data

        """
        if tokens.access_token is None:
            if tokens.refresh_token is None:
                return Payload(user_id=0, user_role=Role.guest, token_type=TokenType.guest_token)

            payload = self._decode(tokens.refresh_token)
            return self._decode(self._update_tokens(response, payload))

        return self._decode(tokens.access_token)

    @classmethod
    def _update_tokens(cls, response: Response, payload: Payload) -> str:
        new_access_token = cls.create(
            Payload(
                user_id=payload.user_id,
                user_role=payload.user_role,
                token_type=TokenType.access_token,
            )
        )
        new_refresh_token = cls.create(
            Payload(
                user_id=payload.user_id,
                user_role=payload.user_role,
                token_type=TokenType.refresh_token,
            )
        )
        new_tokens = TokensCreate(access_token=new_access_token, refresh_token=new_refresh_token)
        cls.set_tokens(new_tokens, response)
        return new_access_token

    @classmethod
    def _decode(cls, token: str) -> Payload:
        try:
            payload_data = jwt.decode(  # type: ignore[reportUnknownMemberType]
                jwt=token,
                key=settings.token.secret_key,
                algorithms=[settings.token.algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise exc.TokenExpiredError from None
        except jwt.InvalidTokenError:
            raise exc.InvalidTokenError from None
        else:
            return Payload(**payload_data)

    @classmethod
    def create(cls, payload: Payload) -> str:
        """
        Encode the jwt token.

        Args:
            payload (Payload): payload data

        Returns:
            str: jwt token

        """
        return jwt.encode(  # type: ignore[reportUnknownMemberType]
            payload=payload.model_dump(),
            key=settings.token.secret_key,
            algorithm=settings.token.algorithm,
        )

    @classmethod
    def set_tokens(cls, tokens: TokensCreate, response: Response) -> None:
        """
        Update the tokens in the cookie.

        Args:
            tokens (TokensCreate): new tokens
            response (Response): response to the client

        """
        response.set_cookie(
            key=TokenType.access_token,
            value=tokens.access_token,
            max_age=settings.token.access_token_expiration,
            httponly=True,
        )
        response.set_cookie(
            key=TokenType.refresh_token,
            value=tokens.refresh_token,
            max_age=settings.token.refresh_token_expiration,
            httponly=True,
        )


class Password:
    context = CryptContext(schemes=["bcrypt"])

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Password and hash verification.

        Args:
            plain_password (str): user's password
            hashed_password (str): hashed password

        Returns:
            bool: comparison status

        """
        return cls.context.verify(plain_password, hashed_password)

    @classmethod
    def hash(cls, password: str) -> str:
        """
        Hash the user's password.

        Args:
            password (str): user's password

        Returns:
            str: hashed password

        """
        return cls.context.hash(password)
