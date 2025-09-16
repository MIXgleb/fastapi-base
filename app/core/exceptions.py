from collections.abc import Sequence
from typing import TypedDict

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError


class TokenExpiredError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token was expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(HTTPException):
    def __init__(self, detail: str = "Invalid token.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenTypeError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, "Invalid token type.")


class AuthorizationError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserExistsError(HTTPException, FileExistsError):
    def __init__(self, detail: str = "User already exists.") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail)


class ResourceNotFoundError(HTTPException, FileNotFoundError):
    def __init__(self, details: str) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, details)


class UserPermissionError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, "Insufficient access rights.")


class ResourceOwnershipError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, "Resource ownership error.")


class WrondMethodError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status.HTTP_405_METHOD_NOT_ALLOWED)


class QueryValueError(RequestValidationError, AttributeError):
    def __init__(self, query_value: str, query_key: str) -> None:
        super().__init__([
            QueryValueError.RequestValidationErrorDict(
                loc=["query", query_key],
                msg=f"There is no '{query_value}' attribute",
                type="wrong_query_value",
            )
        ])

    class RequestValidationErrorDict(TypedDict):
        """Typed dict."""

        loc: Sequence[str]
        msg: str
        type: str


class DatabaseSessionError(OSError):
    def __init__(self) -> None:
        super().__init__("Database session has not been initialized.")
