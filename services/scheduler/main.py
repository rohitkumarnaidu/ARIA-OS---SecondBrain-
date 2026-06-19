import json
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from crons.daily_briefing import run_daily_briefing
from crons.opportunity_radar import run_radar
from crons.weekly_review import run_weekly_review
from crons.habit_checker import run_habit_checker
from crons.missed_task_checker import run_missed_task_checker
from crons.sleep_reminder import run_sleep_reminder
from crons.course_nudge import run_course_nudges
from shared.utils.logger import logger

scheduler = AsyncIOScheduler()


def setup_cron_jobs():
    scheduler.add_job(
        run_daily_briefing,
        trigger=CronTrigger(hour=7, minute=0),
        id="daily_briefing",
        name="Daily Briefing at 7 AM",
        replace_existing=True,
    )

    scheduler.add_job(
        run_radar,
        trigger=CronTrigger(hour=6, minute=0),
        id="opportunity_radar",
        name="Opportunity Radar at 6 AM",
        replace_existing=True,
    )

    scheduler.add_job(
        run_weekly_review,
        trigger=CronTrigger(day_of_week="sun", hour=20, minute=0),
        id="weekly_review",
        name="Weekly Review on Sunday 8 PM",
        replace_existing=True,
    )

    scheduler.add_job(
        run_habit_checker,
        trigger=CronTrigger(hour=20, minute=0),
        id="habit_checker",
        name="Habit Checker at 8 PM",
        replace_existing=True,
    )

    scheduler.add_job(
        run_missed_task_checker,
        trigger=CronTrigger(hour=0, minute=0),
        id="missed_task_checker",
        name="Missed Task Checker at Midnight",
        replace_existing=True,
    )

    scheduler.add_job(
        run_sleep_reminder,
        trigger=CronTrigger(hour=22, minute=30),
        id="sleep_reminder",
        name="Sleep Reminder at 10:30 PM",
        replace_existing=True,
    )

    scheduler.add_job(
        run_course_nudges,
        trigger=CronTrigger(hour=18, minute=0),
        id="course_nudge",
        name="Course Progress Nudge at 6 PM",
        replace_existing=True,
    )

    logger.info("Cron jobs scheduled")
    logger.info("  - Daily Briefing: 7 AM daily")
    logger.info("  - Opportunity Radar: 6 AM daily")
    logger.info("  - Weekly Review: Sunday 8 PM")
    logger.info("  - Habit Checker: 8 PM daily")
    logger.info("  - Missed Task Checker: Midnight daily")
    logger.info("  - Sleep Reminder: 10:30 PM daily")
    logger.info("  - Course Progress Nudge: 6 PM daily")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "scheduler", "jobs": len(scheduler.get_jobs())}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def start_health_server():
    server = HTTPServer(("0.0.0.0", 8001), HealthHandler)
    server.serve_forever()


async def main():
    setup_cron_jobs()
    threading.Thread(target=start_health_server, daemon=True).start()
    scheduler.start()
    logger.info("Scheduler started")
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
