import time
from fastapi import Request
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


async def log_request_time_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(
        f"Request {request.method} {request.url.path} {request.query_params} processed in {process_time:.5f} seconds"
    )
    return response


def register_middlewares(app):
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_time_middleware)
