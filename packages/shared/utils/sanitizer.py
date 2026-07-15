import json
import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

DANGEROUS_PATTERNS = [
    (r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
    (r"javascript\s*:", re.IGNORECASE),
    (r"on\w+\s*=", re.IGNORECASE),
    (r"<iframe[^>]*>", re.IGNORECASE),
    (r"<embed[^>]*>", re.IGNORECASE),
    (r"<object[^>]*>", re.IGNORECASE),
    (r"data\s*:\s*text/html", re.IGNORECASE),
    (r"vbscript\s*:", re.IGNORECASE),
    (r"expression\s*\(.*\)", re.IGNORECASE),
    (r"document\.cookie", re.IGNORECASE),
    (r"document\.write", re.IGNORECASE),
    (r"alert\s*\(", re.IGNORECASE),
    (r"eval\s*\(", re.IGNORECASE),
]


def sanitize_value(value: str) -> str:
    sanitized = value
    for pattern, flags in DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized, flags=flags)
    return sanitized.strip()


def sanitize_dict(d: dict) -> dict:
    result = {}
    for k, v in d.items():
        if isinstance(v, str):
            result[k] = sanitize_value(v)
        elif isinstance(v, dict):
            result[k] = sanitize_dict(v)
        elif isinstance(v, list):
            result[k] = [
                sanitize_dict(i) if isinstance(i, dict) else sanitize_value(i) if isinstance(i, str) else i for i in v
            ]
        else:
            result[k] = v
    return result


class InputSanitizer(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
                sanitized = sanitize_dict(body)
                request._body = json.dumps(sanitized).encode("utf-8")

        response = await call_next(request)
        return response
