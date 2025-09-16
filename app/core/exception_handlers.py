from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.schemas import ProblemDetails, get_custom_errors, get_full_url_data

_JSON_500_RESPONSE = JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={"error": "Internal server error.", "message": "Please try again later."},
)


def validation_exception_handler(request: Request, exc: Exception) -> Response:
    method = request.method
    path = str(request.url)
    client = request.client
    client_ip = client.host if client is not None else "unknown"

    logger_validation_exc = logger.bind(
        path=path,
        method=method,
        client_ip=client_ip,
        headers=request.headers,
    )

    if isinstance(exc, RequestValidationError):
        problem_details = ProblemDetails(
            title="Validation Error",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="One or more validation errors occurred in the request.",
            instance=get_full_url_data(request, exc),
            errors=get_custom_errors(exc),
        )
        logger_validation_exc.bind(type="validation_exception").warning(
            "RequestValidationError: {exc_msg};\nRequest: {method} {path}",
            exc_msg=problem_details.model_dump_json(),
            method=method,
            path=path,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(problem_details),
            headers={"Content-Type": "application/problem+json"},
        )

    logger_validation_exc.bind(type="unexpected_exception").error(
        "UnexpectedException: {exc_msg};\nRequest: {method} {path}",
        exc_msg=repr(exc),
        method=method,
        path=path,
    )
    return _JSON_500_RESPONSE


def http_exception_handler(request: Request, exc: Exception) -> Response:
    method = request.method
    path = str(request.url)
    client = request.client
    client_ip = client.host if client is not None else "unknown"

    logger_fastapi_exc = logger.bind(
        path=path,
        method=method,
        client_ip=client_ip,
        headers=request.headers,
    )

    if isinstance(exc, HTTPException):
        logger_fastapi_exc.bind(type="http_exception", status_code=exc.status_code).warning(
            "HTTPException {status_code}: {exc_msg};\nRequest: {method} {path}",
            status_code=exc.status_code,
            exc_msg=exc.detail,
            method=method,
            path=path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"error": exc.detail}),
        )

    logger_fastapi_exc.bind(type="unexpected_exception").error(
        "UnexpectedException: {exc_msg};\nRequest: {method} {path}",
        exc_msg=repr(exc),
        method=method,
        path=path,
    )
    return _JSON_500_RESPONSE


def database_exception_handler(request: Request, exc: Exception) -> Response:
    method = request.method
    path = str(request.url)
    client = request.client
    client_ip = client.host if client is not None else "unknown"

    logger_db_exc = logger.bind(
        path=path,
        method=method,
        client_ip=client_ip,
        headers=request.headers,
    )

    if isinstance(exc, SQLAlchemyError):
        logger_db_exc.bind(type="sqlalchemy_exception").error(
            "SQLAlchemyException: {exc_msg};\nRequest: {method} {path}",
            exc_msg=repr(exc),
            method=method,
            path=path,
        )
        return _JSON_500_RESPONSE

    logger_db_exc.bind(type="unexpected_exception").error(
        "UnexpectedException: {exc_msg};\nRequest: {method} {path}",
        exc_msg=repr(exc),
        method=method,
        path=path,
    )
    return _JSON_500_RESPONSE


def global_exception_handler(request: Request, exc: Exception) -> Response:
    method = request.method
    path = str(request.url)
    client = request.client
    client_ip = client.host if client is not None else "unknown"

    logger.bind(
        type="unexpected_exception",
        path=path,
        method=method,
        client_ip=client_ip,
        headers=request.headers,
    ).error(
        "UnexpectedException: {exc_msg};\nRequest: {method} {path}",
        exc_msg=repr(exc),
        method=method,
        path=path,
    )
    return _JSON_500_RESPONSE
