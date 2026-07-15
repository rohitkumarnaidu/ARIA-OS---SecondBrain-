from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlparse
from config.core.config import settings
from shared.utils.logger import logger

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in SAFE_METHODS:
            return await call_next(request)

        allowed_origins = [
            o.strip() for o in settings.cors_origins.split(",") if o.strip()
        ]

        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        if origin:
            parsed = urlparse(origin)
            origin_host = f"{parsed.scheme}://{parsed.netloc}".lower()
            if origin_host in allowed_origins or origin in allowed_origins:
                return await call_next(request)
        elif referer:
            parsed = urlparse(referer)
            referer_origin = f"{parsed.scheme}://{parsed.netloc}".lower()
            if referer_origin in allowed_origins:
                return await call_next(request)
        else:
            logger.warn(
                "Non-safe request with no Origin or Referer header",
                method=request.method,
                path=request.url.path,
            )
            return await call_next(request)

        return JSONResponse(
            status_code=403,
            content={
                "detail": "CSRF check failed: Origin/Referer not allowed",
                "error_code": "CSRF_ORIGIN_MISMATCH",
                "request_id": getattr(request.state, "request_id", ""),
            },
        )
