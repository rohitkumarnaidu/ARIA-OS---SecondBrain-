from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio


class RateLimiter(BaseHTTPMiddleware):
    """Simple in-memory rate limiter middleware"""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)

            # Clean old requests
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    req_time
                    for req_time in self.requests[client_ip]
                    if req_time > window_start
                ]
            else:
                self.requests[client_ip] = []

            # Check rate limit
            if len(self.requests[client_ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s",
                )

            # Add current request
            self.requests[client_ip].append(now)

        return await call_next(request)


class EndpointRateLimiter:
    """Per-endpoint rate limiter with different limits"""

    def __init__(self):
        self.limits = {
            "/api/chat": {"max": 30, "window": 60},  # 30 req/min for AI chat
            "/api/tasks": {"max": 60, "window": 60},  # 60 req/min for tasks
            "/api/courses": {"max": 60, "window": 60},
            "/api/goals": {"max": 60, "window": 60},
            "default": {"max": 100, "window": 60},  # 100 req/min default
        }
        self.requests: Dict[str, Dict[str, List[datetime]]] = {}

    def check(self, client_ip: str, endpoint: str) -> bool:
        """Check if request is allowed. Returns True if allowed, False if rate limited."""
        now = datetime.utcnow()
        window = self.limits.get(endpoint, self.limits["default"])
        window_start = now - timedelta(seconds=window["window"])

        # Initialize if needed
        if endpoint not in self.requests:
            self.requests[endpoint] = {}
        if client_ip not in self.requests[endpoint]:
            self.requests[endpoint][client_ip] = []

        # Clean old requests
        self.requests[endpoint][client_ip] = [
            req_time
            for req_time in self.requests[endpoint][client_ip]
            if req_time > window_start
        ]

        # Check limit
        if len(self.requests[endpoint][client_ip]) >= window["max"]:
            return False

        # Add request
        self.requests[endpoint][client_ip].append(now)
        return True


# Global rate limiter instance
endpoint_limiter = EndpointRateLimiter()
