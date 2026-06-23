from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
CSRF_HEADER = "x-csrf-token"


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in SAFE_METHODS:
            return await call_next(request)

        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        if origin or referer:
            csrf_token = request.headers.get(CSRF_HEADER, "")
            if not csrf_token:
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "CSRF token required",
                        "error_code": "CSRF_MISSING",
                        "request_id": getattr(request.state, "request_id", ""),
                    },
                )

        return await call_next(request)
