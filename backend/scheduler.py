from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from crons.daily_briefing import run_daily_briefing
from crons.opportunity_radar import run_radar
from crons.weekly_review import run_weekly_review


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
        trigger=CronTrigger(day_of_week="sunday", hour=20, minute=0),
        id="weekly_review",
        name="Weekly Review on Sunday 8 PM",
        replace_existing=True,
    )

    print("Cron jobs scheduled:")
    print("  - Daily Briefing: 7 AM daily")
    print("  - Opportunity Radar: 6 AM daily")
    print("  - Weekly Review: Sunday 8 PM")


if __name__ == "__main__":
    setup_cron_jobs()
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")

    import asyncio

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
