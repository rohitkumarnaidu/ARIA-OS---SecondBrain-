# API Gateway

---

## Document Control

| Field | Detail |
|---|---|
| **Document ID** | ENG-GTW-001 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | AI Agent System |
| **Date** | 2024-01-01 |
| **Last Reviewed** | 2025-12-15 |
| **Review Cycle** | Quarterly |
| **Approved By** | — |

---

## 1. Executive Summary

Second Brain OS currently routes all client traffic directly to the **FastAPI backend** hosted on Railway, with the **Next.js 14** frontend also served independently. There is no intermediary layer handling cross-cutting concerns like rate limiting, authentication, request transformation, or caching.

As the platform scales to multiple users and potentially multiple backend services (FastAPI API, AI inference server, WebSocket service), a dedicated API gateway layer becomes necessary. This document analyzes the current state, defines gateway responsibilities, evaluates options, and recommends a phased approach: **custom FastAPI middleware** for the alpha phase, graduating to **Vercel Edge Functions** or **Kong** as the platform grows.

---

## 2. Current State

### 2.1 Deployment Architecture (Today)

```
                           Internet
                              │
                 ┌────────────┴────────────┐
                 │                         │
           ┌─────▼─────┐           ┌───────▼──────┐
           │  Next.js   │           │   FastAPI    │
           │   (Vercel) │           │   (Railway)  │
           │ :3000      │           │   :8000      │
           └────────────┘           └──────────────┘
                │                         │
                │               ┌─────────▼─────────┐
                │               │     Supabase       │
                └───────────────┤  (PostgreSQL)      │
                                │                    │
                                └────────────────────┘
```

### 2.2 What's Missing

| Concern | Current State | Why It Matters |
|---|---|---|
| **Rate Limiting** | None | Any client can hammer endpoints |
| **Auth at Edge** | Every route checks auth inline | Wasted compute on invalid requests |
| **Centralized Routing** | Manual URL management | Hard to add services |
| **Request Logging** | Per-service logging | No unified request trail |
| **Caching** | None at network layer | Redundant AI calls |
| **Response Transformation** | Not standardized | Inconsistent error formats |
| **CORS Management** | FastAPI middleware (`CORSMiddleware`) | Works but limited |

### 2.3 Current Routing Table

| Path | Target | Notes |
|---|---|---|
| `/api/*` | FastAPI backend | All API routes |
| `/_next/*` | Next.js static assets | Built files |
| `/static/*` | FastAPI static | Uploaded files (via Supabase Storage) |
| `/` | Next.js | Main application |

---

## 3. API Gateway Responsibilities

### 3.1 Core Responsibilities

| Responsibility | Description | Priority |
|---|---|---|
| **Rate Limiting** | Enforce per-user, per-IP, and per-endpoint request limits | Critical |
| **Authentication** | Validate JWT tokens at the edge before forwarding to backend | Critical |
| **Authorization** | Check role/permission claims from JWT (user, admin) | High |
| **Routing** | Path-based routing to appropriate backend service | High |
| **Request Logging** | Structured logging of every request with duration, status, user ID | High |
| **Response Caching** | Cache idempotent GET responses (briefings, tasks list) | Medium |
| **Request Transformation** | Inject headers (version, request ID), normalize format | Medium |
| **Response Transformation** | Standardize error format, wrap responses | Medium |
| **API Versioning** | Route `/v1/*`, `/v2/*` to different handler versions | Low |
| **Circuit Breaking** | Stop routing to unhealthy backends | Low |
| **WebSocket Termination** | Handle WS connections with sticky sessions | Low |

### 3.2 Responsibilities NOT in Scope

| Responsibility | Reason |
|---|---|
| **Load Balancing** | Railway/Vercel handle this at infrastructure level |
| **SSL Termination** | Handled by Railway/Vercel edge network |
| **DDoS Protection** | Handled by Cloudflare/Vercel firewall |
| **CDN Asset Delivery** | Handled by Vercel Edge Network |

---

## 4. Options Analysis

### 4.1 Option Comparison Matrix

| Option | Type | Latency | Complexity | Cost | Scalability | Best For |
|---|---|---|---|---|---|---|
| **Custom FastAPI Middleware** | Software | ~1ms | Low | Free | Moderate | Alpha / single-region |
| **Vercel Edge Functions** | Edge | ~1ms | Medium | Included | High | Vercel-hosted apps |
| **Express Gateway** | Software | ~5ms | Medium | Free | Moderate | Node.js ecosystems |
| **Kong** | Gateway | ~3ms | High | Free/Paid | High | Multi-service |
| **Traefik** | Reverse proxy | ~2ms | Medium | Free | High | Docker/K8s environments |
| **Nginx** | Reverse proxy | ~1ms | Medium | Free | High | Traditional deployments |
| **AWS API Gateway** | Managed | ~5ms | Low | Pay/use | High | AWS-hosted apps |

### 4.2 Option A: Custom FastAPI Middleware (Recommended for Alpha)

**Pros:**
- Zero additional infrastructure
- Full control over logic
- Same language (Python) as backend
- Simple to implement today

**Cons:**
- Only protects FastAPI, not Next.js routes
- Runs in same process — no fault isolation
- Cannot scale independently from API

### 4.3 Option B: Vercel Edge Functions (Recommended for Beta)

**Pros:**
- Runs at Vercel edge (global, low latency)
- Integrates natively with Next.js
- Rate limiting, auth, and rewrite built-in
- Scales automatically

**Cons:**
- Only for routes routed through Vercel
- 50ms CPU limit per execution
- No direct FastAPI integration (needs rewrite rules)

### 4.4 Option C: Kong API Gateway (Recommended for Production)

**Pros:**
- Enterprise-grade gateway
- Plugins for rate limiting, auth, caching, logging
- Multi-service routing
- Health checks + circuit breaking

**Cons:**
- Requires separate deployment (Docker/ Railway service)
- Operational overhead
- Overkill for single-user alpha

---

## 5. Recommended Architecture

### 5.1 Alpha Phase: Custom FastAPI Middleware

```
                           Internet
                              │
                    ┌─────────▼──────────┐
                    │    Vercel Edge      │
                    │  (Next.js + any    │
                    │   edge middleware)  │
                    └─────────┬──────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
        ┌─────▼──────┐                ┌───────▼───────┐
        │  Next.js    │                │  FastAPI       │
        │  Pages      │                │  + Middleware  │
        └────────────┘                │  Layer         │
                                      │                │
                                      │ ┌────────────┐ │
                                      │ │Rate Limiter│ │
                                      │ ├────────────┤ │
                                      │ │   Auth     │ │
                                      │ ├────────────┤ │
                                      │ │  Logger    │ │
                                      │ ├────────────┤ │
                                      │ │ Response   │ │
                                      │ │ Formatter  │ │
                                      │ └────────────┘ │
                                      └────────────────┘
```

### 5.2 FastAPI Middleware Implementation

```python
# apps/api/app/middleware/gateway.py

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid

class GatewayMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limiter = RateLimiter()

    async def dispatch(self, request: Request, call_next):
        # 1. Request ID injection
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 2. Rate limiting check
        client_ip = request.client.host
        user_id = request.headers.get("X-User-ID", client_ip)
        await self.rate_limiter.check(f"user:{user_id}", limit=100, window=60)

        # 3. Auth validation (skip for public endpoints)
        if not request.url.path.startswith("/api/public/"):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                payload = await verify_jwt(token)
                request.state.user = payload

        # 4. Pre-request logging
        start = time.time()
        logger.info({
            "event": "request_start",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "user_id": user_id,
        })

        # 5. Execute request
        try:
            response: Response = await call_next(request)
            duration = (time.time() - start) * 1000
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time-MS"] = str(round(duration, 2))

            # 6. Post-request logging
            logger.info({
                "event": "request_end",
                "request_id": request_id,
                "status": response.status_code,
                "duration_ms": round(duration, 2),
            })

            return response
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error({
                "event": "request_error",
                "request_id": request_id,
                "error": str(e),
                "duration_ms": round(duration, 2),
            })
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id},
            )

# Register in main.py
app = FastAPI()
app.add_middleware(GatewayMiddleware)
```

### 5.3 Middleware Pipeline Order

```
Request → CORSMiddleware → TrustedHostMiddleware → GatewayMiddleware → Router → Response
                            │
                            ├── RateLimiter
                            ├── AuthValidator
                            ├── RequestLogger
                            └── ResponseFormatter
```

---

## 6. Gateway Routing

### 6.1 Path-Based Routing

| Path Pattern | Target Service | Gateway Action |
|---|---|---|
| `/api/*` | FastAPI (Railway) | Forward with auth check |
| `/api/public/*` | FastAPI (Railway) | Forward without auth |
| `/api/v2/*` | FastAPI (future) | Route to v2 handler |
| `/_next/*` | Next.js static | Serve directly via Vercel |
| `/static/*` | Supabase Storage | Redirect or proxy |
| `/` | Next.js SSR | Serve via Vercel |
| `/ws/*` | WebSocket service (future) | Upgrade to WS connection |

### 6.2 Vercel Rewrite Configuration (for edge routing)

```json
// vercel.json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://api.secondbrain.app/$1"
    },
    {
      "source": "/_next/(.*)",
      "destination": "/_next/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/$1"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "X-Gateway", "value": "vercel-edge" },
        { "key": "X-Request-ID", "value": "uuidv4" }
      ]
    }
  ]
}
```

### 6.3 Nginx Config (for future self-hosted deployment)

```nginx
# infrastructure/nginx/gateway.conf

upstream fastapi_backend {
    server api.railway.internal:8000;
    keepalive 32;
}

upstream nextjs_frontend {
    server nextjs.railway.internal:3000;
    keepalive 32;
}

server {
    listen 443 ssl;
    server_name secondbrain.app;

    # API routes → FastAPI
    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Request-ID $request_id;
        proxy_set_header Authorization $http_authorization;

        limit_req zone=api burst=20 nodelay;
        limit_req_status 429;
    }

    # Static assets → Next.js
    location /_next/ {
        proxy_pass http://nextjs_frontend;
        proxy_set_header Host $host;
    }

    # All other routes → Next.js
    location / {
        proxy_pass http://nextjs_frontend;
        proxy_set_header Host $host;
    }
}
```

---

## 7. Authentication & Authorization

### 7.1 JWT Validation at Gateway

```python
class AuthValidator:
    """Validates JWT at gateway level before forwarding to backend."""

    PUBLIC_PATHS = {
        "/api/public/health",
        "/api/public/auth/login",
        "/api/public/auth/signup",
        "/api/public/auth/callback",
    }

    EXEMPT_METHODS = {"OPTIONS", "HEAD"}

    async def validate(self, request: Request) -> dict | None:
        if request.method in self.EXEMPT_METHODS:
            return None

        if any(request.url.path.startswith(p) for p in self.PUBLIC_PATHS):
            return None

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(401, "Missing Authorization header")

        token = auth_header.replace("Bearer ", "")
        try:
            payload = await supabase_auth.get_user(token)
            request.state.user_id = payload.user.id
            request.state.user_role = payload.user.role or "user"
            return payload
        except Exception:
            raise HTTPException(401, "Invalid or expired token")
```

### 7.2 Role-Based Access Control

| Role | Permissions | Gateway Check |
|---|---|---|
| `anonymous` | Public endpoints only | No token → limited routes |
| `user` | All user endpoints | Valid JWT → full access |
| `admin` | Admin endpoints + user endpoints | JWT with `role=admin` |
| `system` | Internal service-to-service | API key header |

### 7.3 Gateway-Level Authorization Headers

After successful auth validation, the gateway injects verified claims into forwarded requests:

```
X-User-ID: <supabase_user_uuid>
X-User-Role: user | admin
X-Request-ID: <generated_uuid>
X-Gateway-Version: 1.0
```

---

## 8. Rate Limiting

### 8.1 Rate Limit Tiers

| Tier | Limit | Window | Applied To |
|---|---|---|---|
| **Default** | 100 requests | 60 seconds | All authenticated endpoints |
| **Strict** | 20 requests | 60 seconds | AI generation endpoints |
| **Public** | 30 requests | 60 seconds | Unauthenticated endpoints |
| **Admin** | 500 requests | 60 seconds | Admin endpoints |

### 8.2 Rate Limiter Implementation (In-Memory)

```python
class RateLimiter:
    def __init__(self):
        self._buckets: dict[str, list[float]] = defaultdict(list)

    async def check(self, key: str, limit: int, window: int = 60):
        now = time.time()
        window_start = now - window

        # Clean old entries
        self._buckets[key] = [t for t in self._buckets[key] if t > window_start]

        if len(self._buckets[key]) >= limit:
            retry_after = int(self._buckets[key][0] + window - now)
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after_seconds": retry_after,
                    "limit": limit,
                    "window_seconds": window,
                },
                headers={"Retry-After": str(retry_after)},
            )

        self._buckets[key].append(now)
```

### 8.3 Rate Limit Response Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1704067200
```

### 8.4 Distributed Rate Limiting (Future — Redis)

```python
class RedisRateLimiter:
    """Sliding window counter using Redis sorted sets."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def check(self, key: str, limit: int, window: int = 60):
        now = time.time()
        window_start = now - window
        redis_key = f"ratelimit:{key}"

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(redis_key, 0, window_start)
            pipe.zcard(redis_key)
            results = await pipe.execute()

        count = results[1]
        if count >= limit:
            raise HTTPException(429, "Rate limit exceeded")

        await self.redis.zadd(redis_key, {str(now): now})
        await self.redis.expire(redis_key, window)
```

---

## 9. Request/Response Transformation

### 9.1 Request ID Injection

Every request receives a unique ID injected by the gateway:

```python
request.state.request_id = str(uuid.uuid4())
```

All downstream services log this ID for correlation.

### 9.2 Response Standardization

The gateway wraps all responses into a standard envelope:

```json
// Successful response
{
  "status": "success",
  "data": { ... },
  "meta": {
    "request_id": "abc-123-def",
    "timestamp": "2024-01-01T07:00:00.000Z",
    "version": "1.0"
  }
}

// Error response
{
  "status": "error",
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Retry after 42 seconds.",
    "details": { "retry_after_seconds": 42 }
  },
  "meta": {
    "request_id": "abc-123-def",
    "timestamp": "2024-01-01T07:00:00.000Z"
  }
}
```

### 9.3 API Versioning

| Header | Value | Purpose |
|---|---|---|
| `X-API-Version` | `2024-01-01` | Date-based versioning |
| `Accept-Version` | `~1.0` | Semver range |
| `X-API-Deprecated` | `true` | Warning for deprecated versions |

```python
class VersioningMiddleware(BaseHTTPMiddleware):
    SUPPORTED_VERSIONS = {"2024-01-01", "2024-06-01"}
    DEPRECATED_VERSIONS = {"2024-01-01": {"sunset": "2024-12-31", "migration": "/docs/migration-v2"}}

    async def dispatch(self, request, call_next):
        version = request.headers.get("X-API-Version", "2024-06-01")
        if version not in self.SUPPORTED_VERSIONS:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported API version: {version}. Supported: {self.SUPPORTED_VERSIONS}"}
            )

        response = await call_next(request)

        if version in self.DEPRECATED_VERSIONS:
            dep = self.DEPRECATED_VERSIONS[version]
            response.headers["X-API-Deprecated"] = "true"
            response.headers["X-API-Sunset"] = dep["sunset"]
            response.headers["Link"] = f'<{dep["migration"]}>; rel="migration"'

        return response
```

---

## 10. Gateway Monitoring

### 10.1 Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `gateway_requests_total` | Counter | `method`, `path`, `status` | Total requests through gateway |
| `gateway_request_duration_ms` | Histogram | `method`, `path` | Request latency |
| `gateway_rate_limit_hits_total` | Counter | `tier` | Requests blocked by rate limiter |
| `gateway_auth_failures_total` | Counter | `reason` | Auth validation failures |
| `gateway_cache_hits_total` | Counter | `path` | Cache hit count |
| `gateway_cache_misses_total` | Counter | `path` | Cache miss count |
| `gateway_active_connections` | Gauge | — | Concurrent connections |

### 10.2 Logging

```json
{
  "timestamp": "2024-01-01T07:00:00.000Z",
  "level": "INFO",
  "service": "gateway",
  "request_id": "abc-123-def",
  "method": "GET",
  "path": "/api/tasks",
  "status": 200,
  "duration_ms": 145,
  "user_id": "user_abc",
  "rate_limit_remaining": 87,
  "cache_hit": false
}
```

### 10.3 Health Check

```python
@app.get("/api/public/health")
async def gateway_health():
    return {
        "status": "healthy",
        "version": "1.0",
        "uptime_seconds": time.time() - START_TIME,
        "services": {
            "api": await check_service("https://api.railway.internal:8000/health"),
            "supabase": await check_supabase(),
        },
        "rate_limiter": "in_memory" if isinstance(rate_limiter, RateLimiter) else "redis",
        "requests_24h": await get_request_count_24h(),
    }
```

### 10.4 Alerting Thresholds

| Condition | Severity | Action |
|---|---|---|
| p99 latency > 1000ms for 5 min | WARNING | Investigate backend bottleneck |
| Error rate > 5% for 5 min | WARNING | Alert on-call |
| Rate limit hits > 100/hour | INFO | Potential abuse — review |
| Auth failure rate > 10% for 5 min | WARNING | Possible token issue |
| Gateway health check fails | CRITICAL | Page on-call |

---

## 11. Future Migration

### 11.1 Phase Plan

| Phase | Timeline | Gateway | Features |
|---|---|---|---|
| **Alpha** | Now | FastAPI middleware | Rate limiting, auth, logging, request ID |
| **Beta** | Next quarter | Vercel Edge Functions + FastAPI middleware | Edge auth, caching, rewrite rules |
| **Production** | Q3-Q4 | Kong / Nginx | Multi-service routing, circuit breaking, WS termination, service mesh |

### 11.2 Kong Target Architecture

```
                           Internet
                              │
                    ┌─────────▼──────────┐
                    │  Cloudflare/CDN     │
                    │  (DDoS, SSL, cache) │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Kong Gateway     │
                    │  (Docker/Railway)  │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
  ┌─────▼──────┐       ┌──────▼──────┐       ┌─────▼──────┐
  │  FastAPI   │       │  AI Server  │       │ WebSocket  │
  │  (REST)    │       │ (Inference) │       │  Service   │
  └────────────┘       └─────────────┘       └────────────┘
        │                     │
        └────────────┬────────┘
                     │
              ┌──────▼──────┐
              │  Supabase   │
              │ (Postgres)  │
              └─────────────┘
```

### 11.3 Kong Configuration (Future)

```yaml
# infrastructure/kong/kong.yml
_format_version: "3.0"

services:
  - name: api-service
    url: http://fastapi:8000
    routes:
      - name: api-routes
        paths:
          - /api
        methods: [GET, POST, PUT, DELETE, PATCH]
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      - name: key-auth
      - name: cors
      - name: prometheus

  - name: ai-service
    url: http://ai-inference:8080
    routes:
      - name: ai-routes
        paths:
          - /ai
    plugins:
      - name: rate-limiting
        config:
          minute: 20
          policy: local

  - name: websocket-service
    url: http://websocket:4000
    routes:
      - name: ws-routes
        paths:
          - /ws
        protocols: [ws, wss]
```

---

## 12. Appendices

### Appendix A: Gateway Configuration (FastAPI Middleware)

```python
# apps/api/app/middleware/__init__.py

GATEWAY_CONFIG = {
    "rate_limiting": {
        "enabled": True,
        "default_limit": 100,
        "default_window": 60,
        "strict_endpoints": {
            "/api/ai/*": {"limit": 20, "window": 60},
            "/api/auth/*": {"limit": 10, "window": 60},
        },
        "backend": "in_memory",  # or "redis"
    },
    "auth": {
        "enabled": True,
        "jwt_algorithm": "HS256",
        "public_paths": [
            "/api/public/health",
            "/api/public/auth/login",
            "/api/public/auth/signup",
            "/api/public/auth/callback",
        ],
    },
    "logging": {
        "enabled": True,
        "include_body": False,
        "slow_request_threshold_ms": 5000,
    },
    "cors": {
        "allowed_origins": ["https://secondbrain.app", "http://localhost:3000"],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
        "allowed_headers": ["*"],
    },
    "versioning": {
        "enabled": True,
        "default_version": "2024-06-01",
        "supported_versions": ["2024-01-01", "2024-06-01"],
    },
}
```

### Appendix B: Rate Limit Tier Table

| Tier | Limit | Window | Scope | Response Header | Returned On |
|---|---|---|---|---|---|
| `public` | 30 | 60s | IP address | `X-RateLimit-Limit: 30` | Public endpoints |
| `default` | 100 | 60s | User ID | `X-RateLimit-Limit: 100` | Authenticated endpoints |
| `ai` | 20 | 60s | User ID | `X-RateLimit-Limit: 20` | `/api/ai/*` |
| `export` | 5 | 60s | User ID | `X-RateLimit-Limit: 5` | `/api/export/*` |
| `admin` | 500 | 60s | User ID (admin) | `X-RateLimit-Limit: 500` | Admin endpoints |

### Appendix C: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2025-12-15 | AI Agent System | Initial draft |
| — | — | — | — |
| — | — | — | — |
