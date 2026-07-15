import asyncio
import json
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from alerting import alerting
from failure_tracker import failure_tracker
from crons.daily_briefing import run_daily_briefing
from crons.opportunity_radar import run_radar
from crons.weekly_review import run_weekly_review
from crons.habit_checker import run_habit_checker
from crons.missed_task_checker import run_missed_task_checker
from crons.sleep_reminder import run_sleep_reminder
from crons.course_nudge import run_course_nudges
from crons.skill_intelligence_refresh import run_skill_intelligence_refresh
from crons.skill_evidence_expiry import run_skill_evidence_expiry
from crons.skill_analytics_snapshot import run_skill_analytics_snapshot
from crons.skill_mv_refresh import run_skill_mv_refresh
from crons.skill_retention_cleanup import run_skill_retention_cleanup
from crons.deadline_alert import run_deadline_alert
from crons.health_check import run_health_check, HEALTH_STATUS_FILE
from crons.memory_consolidation import run_memory_consolidation
from shared.utils.logger import logger

scheduler = AsyncIOScheduler()


# ── Alerting wrapper ──────────────────────────────────────────────────────────

def _wrap_cron(job_name: str, func):
    """Wrap a cron job with failure tracking and alerting."""
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            await failure_tracker.record_success(job_name)
            duration_ms = (time.time() - start) * 1000
            if duration_ms > 5000:
                logger.info("Cron job completed (slow)", job_name=job_name, duration_ms=round(duration_ms, 2))
            else:
                logger.info("Cron job completed", job_name=job_name, duration_ms=round(duration_ms, 2))
            return result
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            await failure_tracker.record_failure(job_name, str(e))
            await alerting.alert_warning(
                message=f"Cron job failed: {job_name}",
                details={
                    "job_name": job_name,
                    "error_message": str(e),
                    "duration_ms": round(duration_ms, 2),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            return None
    return wrapper


# ── Scheduler event listener (catches missed/unhandled-error jobs) ────────────

async def _scheduler_listener(event):
    job = scheduler.get_job(event.job_id)
    job_name = job.name if job else event.job_id
    if event.code == EVENT_JOB_ERROR:
        await alerting.alert_warning(
            message=f"Unhandled exception in job: {job_name}",
            details={
                "job_name": job_name,
                "error_message": str(getattr(event, "exception", "unknown")),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    elif event.code == EVENT_JOB_MISSED:
        await alerting.alert_warning(
            message=f"Cron job missed its scheduled run: {job_name}",
            details={
                "job_name": job_name,
                "scheduled_run_time": str(getattr(event, "scheduled_run_time", "")),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# ── Cron job registration ─────────────────────────────────────────────────────

JOB_DEFINITIONS = [
    (run_daily_briefing, CronTrigger(hour=7, minute=0), "daily_briefing", "Daily Briefing at 7 AM"),
    (run_radar, CronTrigger(hour=6, minute=0), "opportunity_radar", "Opportunity Radar at 6 AM"),
    (run_weekly_review, CronTrigger(day_of_week="sun", hour=20, minute=0), "weekly_review", "Weekly Review on Sunday 8 PM"),
    (run_habit_checker, CronTrigger(hour=20, minute=0), "habit_checker", "Habit Checker at 8 PM"),
    (run_missed_task_checker, CronTrigger(hour=0, minute=0), "missed_task_checker", "Missed Task Checker at Midnight"),
    (run_sleep_reminder, CronTrigger(hour=22, minute=30), "sleep_reminder", "Sleep Reminder at 10:30 PM"),
    (run_course_nudges, CronTrigger(hour=18, minute=0), "course_nudge", "Course Progress Nudge at 6 PM"),
    (run_skill_intelligence_refresh, CronTrigger(hour=5, minute=0), "skill_intelligence_refresh", "Skill Intelligence Refresh at 5 AM"),
    (run_skill_evidence_expiry, CronTrigger(hour=3, minute=0), "skill_evidence_expiry", "Skill Evidence Expiry Check at 3 AM"),
    (run_skill_analytics_snapshot, CronTrigger(hour=23, minute=30), "skill_analytics_snapshot", "Skill Analytics Daily Snapshot at 11:30 PM"),
    (run_skill_mv_refresh, CronTrigger(hour=4, minute=0), "skill_mv_refresh", "Skill MV Refresh at 4 AM"),
    (run_skill_retention_cleanup, CronTrigger(hour=2, minute=30), "skill_retention_cleanup", "Skill Retention Cleanup at 2:30 AM"),
    (run_deadline_alert, CronTrigger(hour="*", minute=0), "deadline_alert", "Deadline Alert every hour"),
    (run_health_check, CronTrigger(minute="*/5"), "health_check", "Health Check every 5 minutes"),
    (run_memory_consolidation, CronTrigger(day_of_week="sun", hour=2, minute=0), "memory_consolidation", "Weekly Deep Memory Consolidation on Sunday 2 AM"),
]


def setup_cron_jobs():
    for func, trigger, job_id, job_name in JOB_DEFINITIONS:
        scheduler.add_job(
            _wrap_cron(job_id, func),
            trigger=trigger,
            id=job_id,
            name=job_name,
            replace_existing=True,
        )

    scheduler.add_listener(_scheduler_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    logger.info("Cron jobs scheduled", job_count=len(scheduler.get_jobs()))
    for job in scheduler.get_jobs():
        logger.info("Cron job registered", job_id=job.id, job_name=job.name)


# ── Health status file ────────────────────────────────────────────────────────

def write_initial_health():
    """Write a healthy initial health status before first cron run."""
    initial = {
        "status": "healthy",
        "service": "scheduler",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scheduler": {"open_circuits": [], "failing_jobs_count": 0, "total_daily_failures": 0},
        "dependencies": {"supabase": "unknown", "ollama": "unknown"},
    }
    try:
        with open(HEALTH_STATUS_FILE, "w") as f:
            json.dump(initial, f, indent=2)
    except Exception as e:
        logger.warn("Failed to write initial health status", error=str(e))


# ── HTTP Health server ────────────────────────────────────────────────────────

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/health", "/health/ready"):
            health_data = self._load_health()
            if self.path == "/health/ready":
                self.send_response(200 if health_data.get("status") == "healthy" else 503)
            else:
                self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            health_data["jobs"] = len(scheduler.get_jobs())
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _load_health(self) -> dict:
        try:
            if HEALTH_STATUS_FILE.exists():
                with open(HEALTH_STATUS_FILE) as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: could not load health status file: {e}")
        return {"status": "healthy", "service": "scheduler"}

    def log_message(self, format, *args):
        pass


def start_health_server():
    server = HTTPServer(("0.0.0.0", 8001), HealthHandler)
    server.serve_forever()


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    write_initial_health()
    setup_cron_jobs()

    threading.Thread(target=start_health_server, daemon=True).start()

    scheduler.start()

    await alerting.alert_info(
        message="Scheduler started",
        details={
            "job_name": "system",
            "job_count": len(scheduler.get_jobs()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    logger.info("Scheduler started", job_count=len(scheduler.get_jobs()))

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down...")
        await alerting.alert_info(
            message="Scheduler shutting down",
            details={
                "job_name": "system",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        await alerting.flush_pending()
        scheduler.shutdown(wait=False)
        await alerting.shutdown()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
