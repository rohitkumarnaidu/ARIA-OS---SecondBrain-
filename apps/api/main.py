# =============================================================================
# Second Brain OS API — FastAPI Application Entry Point
#
# This file configures the FastAPI application, registers all 31 routers under
# /api/v1/, sets up middleware (CORS, rate limiting, CSRF, GZip, request ID),
# defines health check endpoints, initializes Sentry/Logtail, and starts
# background event processing services.
#
# Router registration table:
#   File                          Prefix
#   ─────────────────────────────────────────────
#   app/api/tasks.py             /api/v1/tasks
#   app/api/courses.py           /api/v1/courses
#   app/api/goals.py             /api/v1/goals
#   app/api/ideas.py             /api/v1/ideas
#   app/api/chat.py              /api/v1/chat
#   app/api/projects.py          /api/v1/projects
#   app/api/resources.py         /api/v1/resources
#   app/api/opportunities.py     /api/v1/opportunities
#   app/api/income.py            /api/v1/income
#   app/api/habits.py            /api/v1/habits
#   app/api/sleep.py             /api/v1/sleep
#   app/api/time.py              /api/v1/time
#   app/api/automation.py        /api/v1/automation
#   app/api/briefings.py         /api/v1/briefings
#   app/api/reviews.py           /api/v1/reviews
#   app/api/memory.py            /api/v1/memory
#   app/api/roadmap.py           /api/v1/roadmap
#   app/api/academics.py         /api/v1/academics
#   app/api/videos.py            /api/v1/videos
#   app/api/analytics.py         /api/v1/analytics
#   app/api/predictions.py       /api/v1/predictions
#   app/api/notifications.py     /api/v1/notifications
#   app/api/nlp.py               /api/v1/nlp
#   app/api/prompts.py           /api/v1/prompts
#   app/api/feedback.py          /api/v1/feedback
#   app/api/monitoring.py        /api/v1/monitoring
#   app/api/data_export.py       /api/v1/data
#   app/api/feature_flags.py     /api/v1/feature-flags
#   app/api/auth.py              /api/v1/auth
#   app/api/skills.py            /api/v1/skills
#   app/api/learning.py          /api/v1/learning
#
# System endpoints (registered inline):
#   GET /                         API status
#   GET /health                   Health check
#   GET /health/live              Liveness probe
#   GET /health/ready             Readiness probe
# =============================================================================

import sys
import uuid
import logging
import time as _time
from pathlib import Path
from contextlib import asynccontextmanager

# Add packages/ to sys.path so all internal imports resolve correctly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from shared.utils.rate_limiter import RateLimiter
from shared.utils.csrf import CSRFMiddleware
from shared.utils.logger import logger, log_request, log_response, _logtail_handler
from shared.utils.cache import cache
from shared.utils.cache_middleware import ResponseCacheMiddleware
from shared.utils.sanitizer import InputSanitizer
from shared.utils.audit import audit_middleware_dispatch, MUTATION_METHODS
from config.core.config import settings

# Import all 31 API routers
from app.api import (
    auth,
    tasks,
    courses,
    goals,
    ideas,
    chat,
    projects,
    resources,
    opportunities,
    income,
    habits,
    sleep,
    time,
    automation,
    briefings,
    reviews,
    memory,
    roadmap,
    academics,
    videos,
    analytics,
    predictions,
    notifications,
    nlp,
    prompts,
    feedback,
    monitoring,
    data_export,
    feature_flags,
    skills,
    learning,
)


# ---------------------------------------------------------------------------
# Application Lifespan (startup/shutdown)
# ---------------------------------------------------------------------------
# The lifespan context manager replaces the deprecated on_startup/on_shutdown
# pattern. It runs once when the app starts and once when it shuts down.
#
# Startup tasks:
#   1. Record start time for uptime calculation
#   2. Initialize Sentry for error tracking (if DSN configured)
#   3. Start Logtail background log flush loop
#   4. Start event outbox and webhook delivery background pollers
#
# Shutdown tasks:
#   1. Gracefully drain pending AI tasks (10s timeout)
#   2. Stop event outbox and webhook delivery pollers
#   3. Clear in-memory caches
#   4. Stop Logtail background flush

@asynccontextmanager
async def lifespan(application: FastAPI):
    import time

    application.state.start_time = time.time()
    logger.info(
        "Second Brain OS API starting",
        version=settings.app_version,
        environment=settings.environment,
        debug=settings.debug,
    )

    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            integrations=[
                FastApiIntegration(),
                HttpxIntegration(),
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
            traces_sample_rate=0.25,
            send_default_pii=False,
        )
        logger.info("Sentry initialized for backend")

    # Start Logtail background flush loop
    _logtail_handler.start_background_flush()

    # Start background event processing services
    try:
        from shared.utils.event_outbox import event_outbox
        from shared.utils.webhook_delivery import webhook_delivery

        await event_outbox.start_background_polling()
        await webhook_delivery.start_background_polling()
        logger.info("Background event outbox and webhook delivery services started")
    except Exception as e:
        logger.warn("Failed to start background event services", error=str(e))

    yield

    # Stop background event processing services
    try:
        from shared.utils.event_outbox import event_outbox
        from shared.utils.webhook_delivery import webhook_delivery

        await event_outbox.stop_background_polling()
        await webhook_delivery.stop_background_polling()
        logger.info("Background event outbox and webhook delivery services stopped")
    except Exception as e:
        logger.warn("Failed to stop background event services", error=str(e))
    logger.info("Second Brain OS API shutting down")

    pending_tasks = getattr(application.state, "pending_ai_tasks", [])
    if pending_tasks:
        logger.info("Awaiting pending AI tasks", count=len(pending_tasks))
        import asyncio

        try:
            await asyncio.wait_for(asyncio.gather(*pending_tasks, return_exceptions=True), timeout=10)
        except asyncio.TimeoutError:
            logger.warn("Some AI tasks did not complete in time", count=len(pending_tasks))

    await cache.clear()
    # Stop Logtail background flush
    await _logtail_handler.stop_background_flush()

    logger.info("Second Brain OS API shutdown complete")


# ---------------------------------------------------------------------------
# FastAPI Application Configuration
# ---------------------------------------------------------------------------
# Title, description, and version are set from settings. OpenAPI tags organize
# the 31 routers into logical groups for the auto-generated docs at /docs.
# The lifespan context manager handles async startup/shutdown tasks.

app = FastAPI(
    title="Second Brain OS API",
    description="Personal AI productivity system for BTech CSE students. "
    "15 modules covering tasks, courses, goals, habits, sleep, income, "
    "projects, ideas, resources, opportunities, time tracking, chat, and automation.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "tasks", "description": "Task CRUD with priority, status, dependencies"},
        {"name": "courses", "description": "Course tracking with progress, deadlines"},
        {"name": "goals", "description": "Goal management with roadmap, milestones"},
        {"name": "habits", "description": "Habit definitions with frequency, streaks"},
        {"name": "sleep", "description": "Sleep tracking with score, debt"},
        {"name": "income", "description": "Income logs with hourly rate"},
        {"name": "projects", "description": "Project phases, blockers, URLs"},
        {"name": "ideas", "description": "Idea pipeline (raw to validating to building)"},
        {"name": "resources", "description": "Resource library with tags"},
        {"name": "opportunities", "description": "Opportunity radar with match scores"},
        {"name": "time", "description": "Time tracking with Pomodoro, deep work"},
        {"name": "chat", "description": "AI chat with ARIA orchestrator"},
        {"name": "automation", "description": "One-click triggers for briefings, radar, reviews"},
        {"name": "briefings", "description": "Daily briefings generated by AI"},
        {"name": "reviews", "description": "Weekly reviews generated by AI"},
        {"name": "memory", "description": "AI persistent memory and preferences"},
        {"name": "roadmap", "description": "Skill development roadmap milestones"},
        {"name": "academics", "description": "Subject and marks tracking"},
        {"name": "videos", "description": "YouTube video vault"},
        {"name": "analytics", "description": "Aggregated productivity stats"},
        {"name": "predictions", "description": "ML-based completion and sleep predictions"},
        {"name": "notifications", "description": "Proactive nudges and alerts"},
        {"name": "nlp", "description": "Natural language command parsing"},
        {"name": "prompts", "description": "Prompt file inspection and rendering"},
        {"name": "feedback", "description": "User feedback collection and summary"},
        {"name": "monitoring", "description": "Token usage and cost tracking"},
        {"name": "auth", "description": "Authentication, token refresh, and API key rotation"},
        {"name": "data", "description": "GDPR data export and data management"},
        {
            "name": "skills",
            "description": "Skills taxonomy, user skills, evidence, market intelligence, and learning paths",
        },
        {"name": "learning", "description": "Learning insights and pattern detection from ARIA Learning Agent"},
        {"name": "system", "description": "Health check and system endpoints"},
    ],
)

# ---------------------------------------------------------------------------
# Middleware Stack (executed in registration order)
# ---------------------------------------------------------------------------
# 1. ResponseCacheMiddleware — In-memory GET response caching (optional)
# 2. RateLimiter            — Sliding-window IP-based rate limiting (100 req/min)
# 3. CORSMiddleware         — Cross-Origin Resource Sharing (configurable origins)
# 4. InputSanitizer         — Sanitize POST/PUT/PATCH JSON bodies (XSS prevention)
# 5. GZipMiddleware         — Response compression for bodies >1000 bytes
# 6. CSRFMiddleware         — CSRF token validation for state-changing requests
#
# Custom middleware (below, registered with @app.middleware):
# 7. request_id_middleware     — X-Request-ID header generation + audit logging
# 8. cache_control_middleware  — Cache-Control + security headers

app.add_middleware(ResponseCacheMiddleware, default_ttl=60, max_size=256)

app.add_middleware(
    RateLimiter,
    max_requests=settings.rate_limit_max,
    window_seconds=settings.rate_limit_window,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(InputSanitizer)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(CSRFMiddleware)


# ---------------------------------------------------------------------------
# Middleware: Request ID + Audit Trail
# ---------------------------------------------------------------------------
# Generates or propagates an X-Request-ID header for every request. Logs
# request start/end with duration tracking. On mutation methods (POST, PUT,
# PATCH, DELETE), dispatches an audit event if the user is authenticated.
# Catches unhandled exceptions and returns a structured 500 error.

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    request.state.start_time = _time.time()

    log_request(
        endpoint=str(request.url.path),
        method=request.method,
        request_id=request_id,
    )

    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (_time.time() - request.state.start_time) * 1000
        logger.error(
            "Unhandled request exception",
            path=str(request.url.path),
            method=request.method,
            duration_ms=duration_ms,
            request_id=request_id,
            error=str(exc),
        )
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "request_id": request_id,
                "timestamp": _time.time(),
            },
            headers={"X-Request-ID": request_id},
        )

    response.headers["X-Request-ID"] = request_id

    duration_ms = (_time.time() - request.state.start_time) * 1000
    log_response(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )

    if request.method in MUTATION_METHODS and response.status_code < 400:
        user_id = None
        if hasattr(request.state, "user"):
            user_id = getattr(request.state.user, "id", None)
        if user_id:
            await audit_middleware_dispatch(request, response, user_id=user_id, duration_ms=duration_ms)

    return response


# ---------------------------------------------------------------------------
# Middleware: Cache-Control + Security Headers
# ---------------------------------------------------------------------------
# Sets Cache-Control headers based on path prefix:
#   /static/, /assets/  → immutable, 1 year
#   /health             → no-store (never cache)
#   GET requests        → private, 60s, stale-while-revalidate=300
#   Other               → no-store
# Also sets security headers: X-Content-Type-Options, X-Frame-Options, XSS

@app.middleware("http")
async def cache_control_middleware(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path

    if path.startswith("/static/") or path.startswith("/assets/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    elif path.startswith("/health"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    elif request.method == "GET":
        response.headers["Cache-Control"] = "private, max-age=60, stale-while-revalidate=300"
    else:
        response.headers["Cache-Control"] = "no-store, must-revalidate"

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: blob: https:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    return response


# ---------------------------------------------------------------------------
# Router Registration (31 routers under /api/v1/)
# ---------------------------------------------------------------------------
# All routers accept auth via get_current_user dependency unless noted.
# Each router's endpoints are documented in docs/engineering/api/openapi-reference.md.

app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(ideas.router, prefix="/api/v1/ideas", tags=["ideas"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(opportunities.router, prefix="/api/v1/opportunities", tags=["opportunities"])
app.include_router(income.router, prefix="/api/v1/income", tags=["income"])
app.include_router(habits.router, prefix="/api/v1/habits", tags=["habits"])
app.include_router(sleep.router, prefix="/api/v1/sleep", tags=["sleep"])
app.include_router(time.router, prefix="/api/v1/time", tags=["time"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
app.include_router(briefings.router, prefix="/api/v1/briefings", tags=["briefings"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(roadmap.router, prefix="/api/v1/roadmap", tags=["roadmap"])
app.include_router(academics.router, prefix="/api/v1/academics", tags=["academics"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(nlp.router, prefix="/api/v1/nlp", tags=["nlp"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(data_export.router, prefix="/api/v1/data", tags=["data"])
app.include_router(feature_flags.router, prefix="/api/v1/feature-flags", tags=["feature_flags"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["learning"])


# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------
# Catch-all for unhandled exceptions at the application level. Returns a
# structured 500 error with a request ID for tracing. The request_id_middleware
# also has its own exception handler for middleware-level errors.

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(
        "Global unhandled exception",
        path=str(request.url.path),
        error=str(exc),
        error_type=type(exc).__name__,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


# ---------------------------------------------------------------------------
# System Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["system"])
async def root():
    """Return basic API status information (version, environment, docs URL)."""
    return {
        "message": "Second Brain OS API is running",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
async def health_check():
    """Return overall health status, uptime, and registered endpoint count."""
    total_endpoints = len(app.routes)
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": _time.time(),
        "uptime_secs": _time.time() - getattr(app.state, "start_time", _time.time()),
        "endpoints_registered": total_endpoints,
    }


@app.get("/health/ready", tags=["system"])
async def readiness_check():
    """Readiness probe — checks Supabase and AI provider connectivity."""
    deps = {
        "api": {"status": "ok"},
    }
    try:
        from config.core.supabase import get_supabase_client

        supabase = get_supabase_client()
        supabase.from_("users").select("count", count="exact").limit(1).execute()
        deps["supabase"] = {"status": "ok"}
    except Exception as e:
        deps["supabase"] = {"status": "error", "detail": str(e)}

    if settings.use_local_ai:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code == 200:
                    deps["ollama"] = {"status": "ok"}
                else:
                    deps["ollama"] = {"status": "degraded"}
        except Exception as e:
            deps["ollama"] = {"status": "unavailable", "detail": str(e)}
    else:
        deps["claude_api"] = {"status": "configured" if settings.claude_api_key else "not_configured"}

    all_ok = all(d.get("status") in ("ok", "configured", "not_configured") for d in deps.values())
    overall = "healthy" if all_ok else "degraded"

    return {
        "status": overall,
        "version": settings.app_version,
        "dependencies": deps,
    }


@app.get("/health/live", tags=["system"])
async def liveness_check():
    """Liveness probe — returns 200 if the process is alive."""
    return {"status": "alive"}
