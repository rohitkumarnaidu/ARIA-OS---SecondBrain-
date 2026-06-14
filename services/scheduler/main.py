import sys
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

    print("Cron jobs scheduled:")
    print("  - Daily Briefing: 7 AM daily")
    print("  - Opportunity Radar: 6 AM daily")
    print("  - Weekly Review: Sunday 8 PM")
    print("  - Habit Checker: 8 PM daily")
    print("  - Missed Task Checker: Midnight daily")
    print("  - Sleep Reminder: 10:30 PM daily")
    print("  - Course Progress Nudge: 6 PM daily")


if __name__ == "__main__":
    setup_cron_jobs()
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")

    import asyncio

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")