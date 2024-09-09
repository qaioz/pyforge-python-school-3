import json
import time
from fastapi import Request
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, JSONResponse

from src.redis import get_redis_cache_service
import fnmatch

logger = logging.getLogger(__name__)


async def log_request_time_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(
        f"Request {request.method} {request.url.path} {request.query_params} processed in {process_time:.5f} seconds"
    )
    return response


async def caching_middleware(request: Request, call_next):
    # this is a dictionary of endpoints that should be cached with their respective expiration time
    cached_endpoints = {"**/molecules/**": 60 * 60 * 24 * 7}

    if request.method != "GET":
        logger.info(
            f"Request {request.url.path} is not cached because it is not a GET request"
        )
        return await call_next(request)

    if not any(
        fnmatch.fnmatch(request.url.path, endpoint) for endpoint in cached_endpoints
    ):
        logger.info(f"Request {request.url.path} is not cached")
        return await call_next(request)

    url = request.url.path
    params = sorted(request.query_params.items())
    cache_key = url + "?" + "&".join([f"{k}={v}" for k, v in params])

    cached_response = get_redis_cache_service().get_json(cache_key)
    if cached_response:
        logger.info(f"cache hit for {cache_key}")
        if "no-cache" not in request.headers.get("cache-control", {}):
            return JSONResponse(
                content=cached_response["body"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
            )
        logger.info(f"no-cache header found, revalidating cache for {cache_key}")
    else:
        logger.info(f"cache miss for {cache_key}")

    response = await call_next(request)

    # Looks like fastapi always returns a StreamingResponse for responses that are not JSONResponse
    # I could not find exact documentation on this, but this is what I observed
    # So, I implemented a logic just for caching StreamingResponse
    # because extracting the body from StreamingResponse is a bit different than JSONResponse and other responses
    if not isinstance(response, StreamingResponse):
        logger.info(f"Response for {cache_key} is not a StreamingResponse, not caching")
        return response

    response_body = b"".join([chunk async for chunk in response.body_iterator])
    response_json = json.loads(response_body.decode())
    headers = dict(response.headers)
    headers.pop("content-length")

    # Cache the response
    cache_data = {
        "body": response_json,
        "status_code": response.status_code,
        "headers": headers,
    }
    get_redis_cache_service().set_json(cache_key, cache_data)

    # Return the original response
    return JSONResponse(
        content=response_json, status_code=response.status_code, headers=headers
    )


def register_middlewares(app):
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_time_middleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=caching_middleware)
