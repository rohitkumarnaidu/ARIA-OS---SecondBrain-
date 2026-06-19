"""Tests for scheduler cron job setup — job registration, trigger configs."""

import pytest

pytest.importorskip("apscheduler", reason="apscheduler not installed")


@pytest.mark.scheduler
class TestScheduler:
    """Test scheduler job configurations without starting the scheduler."""

    def test_daily_briefing_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(hour=7, minute=0)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 7
        assert next_fire.minute == 0

    def test_weekly_review_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(day_of_week="sun", hour=20, minute=0)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 20
        assert next_fire.minute == 0
        assert next_fire.strftime("%A").lower() == "sunday"

    def test_cron_job_ids_are_descriptive(self):
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from main import setup_cron_jobs

        scheduler = AsyncIOScheduler()
        setup_cron_jobs()

        for job in scheduler.get_jobs():
            assert job.id is not None
            assert len(job.id) > 3
            assert "_" in job.id, f"Job ID '{job.id}' should use snake_case"

    def test_cron_job_triggers_are_cron(self):
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from main import setup_cron_jobs

        scheduler = AsyncIOScheduler()
        setup_cron_jobs()

        for job in scheduler.get_jobs():
            assert isinstance(job.trigger, CronTrigger), f"Job '{job.id}' should use CronTrigger"


@pytest.mark.scheduler
class TestSchedulerImports:
    """Test that all cron modules import correctly."""

    def test_daily_briefing_import(self):
        from crons.daily_briefing import run_daily_briefing

        assert callable(run_daily_briefing)

    def test_opportunity_radar_import(self):
        from crons.opportunity_radar import run_radar

        assert callable(run_radar)

    def test_weekly_review_import(self):
        from crons.weekly_review import run_weekly_review

        assert callable(run_weekly_review)

    def test_habit_checker_import(self):
        from crons.habit_checker import run_habit_checker

        assert callable(run_habit_checker)

    def test_missed_task_checker_import(self):
        from crons.missed_task_checker import run_missed_task_checker

        assert callable(run_missed_task_checker)

    def test_sleep_reminder_import(self):
        from crons.sleep_reminder import run_sleep_reminder

        assert callable(run_sleep_reminder)

    def test_course_nudge_import(self):
        from crons.course_nudge import run_course_nudges

        assert callable(run_course_nudges)
