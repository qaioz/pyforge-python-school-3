import json
import time
from fastapi import Request
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, JSONResponse

from src.redis import get_redis_cache_service
import fnmatch

logger = logging.getLogger(__name__)

CACHED_CONTENT_LENGTH_LIMIT = 1024 * 1024


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
    cached_endpoints = {
        "**/molecules/**": 60 * 60 * 24 * 7
    }

    if request.method != "GET":
        logger.info(
            "Request is not cached because it is not a GET request"
        )
        return await call_next(request)

    # fnmatch is used to match the request URL with the cached endpoints, it supports unix shell-style wildcards
    if not any(
        fnmatch.fnmatch(request.url.path, endpoint) for endpoint in cached_endpoints
    ):
        logger.info(f"URL {request.url.path} is not cached")
        return await call_next(request)

    url = request.url.path

    # sorting the query params is super important because the order of query params does not matter
    # if we do not do this, the cache key will be different for the same URL with different query params
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

    if response.status_code != 200:
        logger.info(f"Response for {cache_key} is not 200, not caching")
        return response

    # Looks like fastapi always returns a StreamingResponse for responses that are not JSONResponse
    # I could not find exact documentation on this, but this is what I observed
    # So, I implemented a logic just for caching StreamingResponse
    # because extracting the body from StreamingResponse is a bit different than JSONResponse and other responses
    if not isinstance(response, StreamingResponse):
        logger.info(f"Response for {cache_key} is not a StreamingResponse, not caching")
        return response

    # What I am doing I am reading the content of the StreamingResponse and then converting it to JSONResponse
    # This can cause several concerns.
    # 1. If the response is too large, it will consume a lot of memory
    # 2. There is a possibility of mismatch in the response content-length header and the actual content length

    # I had the second problem and I just removed the content-length header from the response headers, fortunately
    # fastapi automatically recalculates the content-length header

    # For the first problem, I think you can not get away with caching and not buffering the response,
    # what you can do is to limit the size of the response that you are caching, by reading the response content-length

    # This is just and arbitrary limit, can be changed according to the memory available
    if int(response.headers.get("content-length", 0)) > CACHED_CONTENT_LENGTH_LIMIT:
        logger.info(f"Response for {cache_key} is too large, not caching")
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

    # Remember, the reason we are converting the StreamingResponse to JSONResponse is because the StreamingResponse is
    # already consumed because we read it to cache it
    return JSONResponse(
        content=response_json, status_code=response.status_code, headers=headers
    )


def register_middlewares(app):
    app.add_middleware(BaseHTTPMiddleware, dispatch=caching_middleware)
    # request time logging middleware should be added last
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_time_middleware)
