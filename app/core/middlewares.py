import time
from typing import override

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class LoggingMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        method = request.method
        path = request.url.path
        client = request.client
        client_ip = client.host if client is not None else "unknown"

        logger_request = logger.bind(
            path=path,
            method=method,
            client_ip=client_ip,
            cookies=request.cookies,
        )
        logger_request.bind(
            type="request",
            headers=request.headers,
        ).info(
            "Request: {method} {path} from {client_ip}",
            method=method,
            path=path,
            client_ip=client_ip,
        )

        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        logger_request.bind(
            type="response",
            headers=response.headers,
            process_time=str(process_time),
        ).info(
            "Response: {method} {path} returned {status_code} to {client_ip}",
            method=method,
            path=path,
            status_code=response.status_code,
            client_ip=client_ip,
        )
        return response
