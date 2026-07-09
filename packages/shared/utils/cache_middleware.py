from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from typing import Set
import hashlib
from shared.utils.cache import cache


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """Cache GET responses in-memory with TTL for cache-control-respecting endpoints."""

    def __init__(self, app, default_ttl: int = 60, max_size: int = 256):
        super().__init__(app)
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._skip_paths: Set[str] = {"/health", "/metrics", "/api/v1/chat"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method != "GET":
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in self._skip_paths):
            return await call_next(request)

        if "no-cache" in request.headers.get("cache-control", ""):
            return await call_next(request)

        cache_key = self._cache_key(request)
        cached = await cache.get(cache_key)
        if cached is not None:
            resp = Response(
                content=cached["body"],
                status_code=cached["status"],
                media_type=cached["media_type"],
                headers=cached["headers"],
            )
            resp.headers["X-Cache"] = "HIT"
            return resp

        response = await call_next(request)

        if response.status_code < 400 and int(response.headers.get("content-length", "0")) < 51200:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            headers = dict(response.headers)
            headers["X-Cache"] = "MISS"
            await cache.set(
                cache_key,
                {
                    "body": body,
                    "status": response.status_code,
                    "media_type": response.media_type,
                    "headers": headers,
                },
                ttl=self.default_ttl,
            )
            return Response(
                content=body, status_code=response.status_code, media_type=response.media_type, headers=headers
            )

        return response

    @staticmethod
    def _cache_key(request: Request) -> str:
        raw = f"{request.method}:{request.url.path}:{sorted(request.query_params.items())}"
        return f"rm:{hashlib.md5(raw.encode()).hexdigest()}"
