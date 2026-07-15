"""Health check cron job — runs every 5 minutes to verify scheduler health."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

from failure_tracker import failure_tracker
from alerting import alerting
from shared.utils.logger import logger

HEALTH_STATUS_FILE = Path(__file__).resolve().parent.parent / "scheduler_health.json"


async def run_health_check():
    """Verify scheduler health and dependencies, write status file."""
    tracker_summary = await failure_tracker.get_summary()
    open_circuits = tracker_summary.get("open_circuits", [])
    failing_jobs = tracker_summary.get("failing_jobs", [])

    # ── Supabase ──────────────────────────────────────────────────────────
    supabase_ok = False
    try:
        from config.core.supabase import get_supabase_client

        supabase = get_supabase_client()
        supabase.from_("users").select("count", count="exact").limit(1).execute()
        supabase_ok = True
    except Exception as e:
        logger.warn("Health check: Supabase unavailable", error=str(e))

    # ── Ollama (optional) ─────────────────────────────────────────────────
    ollama_ok: bool | None = None  # None = not configured
    try:
        if os.getenv("USE_LOCAL_AI", "True").lower() == "true":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{base_url}/api/tags")
                ollama_ok = resp.status_code == 200
    except Exception:
        ollama_ok = False

    open_circuits_bad = len(open_circuits) > 0
    overall_status = "degraded" if (open_circuits_bad or not supabase_ok) else "healthy"

    health = {
        "status": overall_status,
        "service": "scheduler",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scheduler": {
            "open_circuits": open_circuits,
            "failing_jobs_count": len(failing_jobs),
            "total_daily_failures": tracker_summary.get("total_daily_failures", 0),
        },
        "dependencies": {
            "supabase": "ok" if supabase_ok else "error",
            "ollama": "ok" if ollama_ok is True else ("unavailable" if ollama_ok is False else "not_configured"),
        },
    }

    try:
        with open(HEALTH_STATUS_FILE, "w") as f:
            json.dump(health, f, indent=2)
    except Exception as e:
        logger.error("Failed to write health status file", error=str(e))

    logger.info("Health check completed", status=overall_status, failing_jobs=len(failing_jobs))

    if open_circuits:
        await alerting.alert_warning(
            message="Scheduler health degraded: circuit breakers open",
            details={
                "job_name": "health_check",
                "open_circuits": ", ".join(open_circuits),
                "failed_dependency": "supabase" if not supabase_ok else "none",
                "timestamp": health["timestamp"],
            },
        )
