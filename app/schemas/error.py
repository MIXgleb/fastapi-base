from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    field: list[str]
    message: str
    type: str


class ProblemDetails(BaseModel):
    type: str = Field(
        default="about:blank",
        description="A URI reference that identifies the problem type",
    )
    title: str
    status: int
    detail: str
    instance: dict[str, Any]
    errors: list[ValidationErrorDetail] | None = None


def get_custom_errors(exc: RequestValidationError) -> list[ValidationErrorDetail]:
    """
    Convert the error descriptions to the custom type.

    Args:
        exc (RequestValidationError): exception instance

    Returns:
        list[ValidationErrorDetail]: custom error description list

    """
    return [
        ValidationErrorDetail(field=error["loc"], message=error["msg"], type=error["type"])
        for error in exc.errors()
    ]


def get_full_url_data(request: Request, exc: Exception) -> dict[str, Any]:
    """
    Get the full URL details.

    Args:
        request (Request): request instance
        exc (Exception): exception instance

    Returns:
        dict[str, Any]: url instance data

    """
    instance: dict[str, Any] = {"method": request.method, "path": request.url.path}

    if path_params := request.path_params:
        instance["params"] = path_params

    if query_params := request.query_params:
        dict_query: dict[str, Any] = {}

        for q in str(query_params).split("&"):
            k, v = q.split("=")

            if k in dict_query:
                cur: str | list[str] = dict_query[k]
                dict_query[k] = [*cur, v] if isinstance(cur, list) else [cur, v]
            else:
                dict_query[k] = v

        instance["query"] = dict_query

    body_key = "body"

    if hasattr(exc, body_key) and getattr(exc, body_key):
        instance["body"] = getattr(exc, body_key)

    return instance
