import sys
import uuid
import time
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from shared.utils.rate_limiter import RateLimiter
from shared.utils.logger import logger, log_request, log_response
from shared.utils.cache import cache
from config.core.config import settings
from app.api import (
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
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info(
        "Second Brain OS API starting",
        version=settings.app_version,
        environment=settings.environment,
        debug=settings.debug,
    )
    yield
    logger.info("Second Brain OS API shutting down")
    await cache.clear()


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
    ],
)

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


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    request.state.start_time = time.time()

    log_request(
        endpoint=str(request.url.path),
        method=request.method,
        request_id=request_id,
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    duration_ms = (time.time() - request.state.start_time) * 1000
    log_response(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )

    return response


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


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "Second Brain OS API is running",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time(),
    }


@app.get("/health/ready", tags=["system"])
async def readiness_check():
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
            import asyncio
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

    all_ok = all(
        d.get("status") in ("ok", "configured", "not_configured") for d in deps.values()
    )
    overall = "healthy" if all_ok else "degraded"

    return {
        "status": overall,
        "version": settings.app_version,
        "dependencies": deps,
    }


@app.get("/health/live", tags=["system"])
async def liveness_check():
    return {"status": "alive"}
