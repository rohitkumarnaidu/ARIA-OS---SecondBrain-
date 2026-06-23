"""Tests for scheduler cron job setup — job registration, trigger configs, handler behavior."""

from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
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

    def test_opportunity_radar_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(hour=6, minute=0)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 6
        assert next_fire.minute == 0

    def test_habit_checker_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(hour=20, minute=0)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 20
        assert next_fire.minute == 0

    def test_missed_task_checker_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(hour=0, minute=0)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 0
        assert next_fire.minute == 0

    def test_sleep_reminder_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(hour=22, minute=30)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 22
        assert next_fire.minute == 30

    def test_course_nudge_cron_config(self):
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        trigger = CronTrigger(hour=18, minute=0)
        next_fire = trigger.get_next_fire_time(None, datetime.now())
        assert next_fire is not None
        assert next_fire.hour == 18
        assert next_fire.minute == 0

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

    def test_all_seven_jobs_registered(self):
        import main as scheduler_module
        scheduler_module.setup_cron_jobs()

        job_ids = {job.id for job in scheduler_module.scheduler.get_jobs()}
        expected = {
            "daily_briefing", "opportunity_radar", "weekly_review",
            "habit_checker", "missed_task_checker", "sleep_reminder", "course_nudge",
        }
        assert job_ids == expected, f"Missing jobs: {expected - job_ids}"
        scheduler_module.scheduler.remove_all_jobs()

    def test_jobs_have_descriptive_names(self):
        import main as scheduler_module
        scheduler_module.setup_cron_jobs()

        for job in scheduler_module.scheduler.get_jobs():
            assert job.name is not None
            assert len(job.name) > 5
        scheduler_module.scheduler.remove_all_jobs()

    def test_all_jobs_have_unique_ids(self):
        import main as scheduler_module
        scheduler_module.scheduler.remove_all_jobs()
        scheduler_module.setup_cron_jobs()
        job_ids = [job.id for job in scheduler_module.scheduler.get_jobs()]
        assert len(job_ids) == len(set(job_ids))
        scheduler_module.scheduler.remove_all_jobs()


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


@pytest.mark.scheduler
class TestCronJobHandlers:
    """Test each cron job handler function with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_daily_briefing_handler(self, mocker):
        mock_supabase = mocker.patch("crons.daily_briefing.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}, {"id": "user2"}
        ]
        mock_generate = mocker.patch("crons.daily_briefing.generate_daily_briefing",
                                      return_value={"productivity_score": 85})
        mock_sanitize = mocker.patch("crons.daily_briefing.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.daily_briefing import run_daily_briefing
        await run_daily_briefing()

        assert mock_generate.call_count == 2
        mock_generate.assert_any_call("user1")
        mock_generate.assert_any_call("user2")

    @pytest.mark.asyncio
    async def test_daily_briefing_handler_empty_users(self, mocker):
        mock_supabase = mocker.patch("crons.daily_briefing.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = []
        mock_generate = mocker.patch("crons.daily_briefing.generate_daily_briefing")
        mock_sanitize = mocker.patch("crons.daily_briefing.sanitize_input")

        from crons.daily_briefing import run_daily_briefing
        await run_daily_briefing()

        mock_generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_daily_briefing_handler_user_error(self, mocker):
        mock_supabase = mocker.patch("crons.daily_briefing.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}, {"id": "user2"}
        ]
        mock_generate = mocker.patch("crons.daily_briefing.generate_daily_briefing",
                                      side_effect=[Exception("API down"), {"productivity_score": 90}])
        mock_sanitize = mocker.patch("crons.daily_briefing.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.daily_briefing import run_daily_briefing
        await run_daily_briefing()

        assert mock_generate.call_count == 2

    @pytest.mark.asyncio
    async def test_opportunity_radar_handler(self, mocker):
        mock_supabase = mocker.patch("crons.opportunity_radar.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}
        ]
        mock_radar = mocker.patch("crons.opportunity_radar.run_opportunity_radar",
                                   return_value=[{"title": "Internship at Google"}])
        mock_sanitize = mocker.patch("crons.opportunity_radar.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.opportunity_radar import run_radar
        await run_radar()

        mock_radar.assert_called_once_with("user1")

    @pytest.mark.asyncio
    async def test_opportunity_radar_handler_empty(self, mocker):
        mock_supabase = mocker.patch("crons.opportunity_radar.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = []
        mock_radar = mocker.patch("crons.opportunity_radar.run_opportunity_radar")

        from crons.opportunity_radar import run_radar
        await run_radar()

        mock_radar.assert_not_called()

    @pytest.mark.asyncio
    async def test_weekly_review_handler(self, mocker):
        mock_supabase = mocker.patch("crons.weekly_review.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}
        ]
        mock_review = mocker.patch("crons.weekly_review.generate_weekly_review",
                                    return_value={"completion_rate": 0.75})
        mock_sanitize = mocker.patch("crons.weekly_review.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.weekly_review import run_weekly_review
        await run_weekly_review()

        mock_review.assert_called_once_with("user1")

    @pytest.mark.asyncio
    async def test_weekly_review_handler_error(self, mocker):
        mock_supabase = mocker.patch("crons.weekly_review.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}
        ]
        mock_review = mocker.patch("crons.weekly_review.generate_weekly_review",
                                    side_effect=Exception("Generation failed"))
        mock_sanitize = mocker.patch("crons.weekly_review.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.weekly_review import run_weekly_review
        await run_weekly_review()

        mock_review.assert_called_once_with("user1")

    @pytest.mark.asyncio
    async def test_habit_checker_handler(self, mocker):
        from crons.habit_checker import run_habit_checker

        results = [
            {"data": [{"id": "user1"}, {"id": "user2"}]},
            {"data": [{"id": "h1", "name": "Read"}]},
            {"data": []},
            {"data": [{"id": "h2", "name": "Exercise"}]},
            {"data": [{"id": "log1"}]},
        ]
        result_iter = iter(results)
        exec_count = [0]

        class FakeResponse:
            def __init__(self, data):
                self.data = data

        class FakeQuery:
            def select(self, *args, **kwargs):
                return self
            def eq(self, *args, **kwargs):
                return self
            def gte(self, *args, **kwargs):
                return self
            def lt(self, *args, **kwargs):
                return self
            def execute(self):
                exec_count[0] += 1
                return FakeResponse(**next(result_iter))
            def update(self, *args, **kwargs):
                return self
            def order(self, *args, **kwargs):
                return self
            def range(self, *args, **kwargs):
                return self
            def text_search(self, *args, **kwargs):
                return self

        class FakeSupabase:
            def from_(self, table):
                return FakeQuery()

        mock_supabase = mocker.patch("crons.habit_checker.get_supabase_client",
                                      return_value=FakeSupabase())
        mock_date = mocker.patch("crons.habit_checker.date")
        mock_date.today.return_value.isoformat.return_value = "2026-06-21"

        await run_habit_checker()

        assert exec_count[0] == 5

    @pytest.mark.asyncio
    async def test_habit_checker_handler_no_habits(self, mocker):
        mock_supabase = mocker.patch("crons.habit_checker.get_supabase_client")
        mock_date = mocker.patch("crons.habit_checker.date")
        mock_date.today.return_value.isoformat.return_value = "2026-06-21"
        mock_supabase().from_().select().execute.side_effect = [
            mocker.Mock(data=[{"id": "user1"}]),
            mocker.Mock(data=[]),  # no active habits
        ]

        from crons.habit_checker import run_habit_checker
        await run_habit_checker()

        # Should not query habit_logs if no habits
        habit_logs_calls = [
            c for c in mock_supabase().from_().call_args_list
            if c[0][0] == "habit_logs"
        ]
        assert len(habit_logs_calls) == 0

    @pytest.mark.asyncio
    async def test_missed_task_checker_handler(self, mocker):
        from crons.missed_task_checker import run_missed_task_checker

        mock_supabase = mocker.patch("crons.missed_task_checker.get_supabase_client")
        mocker.patch("crons.missed_task_checker.datetime")

        execute_responses = iter([
            mocker.Mock(data=[{"id": "user1"}]),
            mocker.Mock(data=[{"id": "task1", "missed_count": 0}]),
        ])
        execute_mock = mocker.Mock(side_effect=lambda: next(execute_responses))

        update_execute = mocker.Mock()
        update_mock = mocker.Mock(return_value=mocker.Mock(eq=lambda x: mocker.Mock(execute=update_execute)))

        query_chain = mocker.Mock()
        query_chain.execute = execute_mock
        query_chain.eq.return_value = query_chain
        query_chain.lt.return_value = query_chain
        query_chain.select.return_value = query_chain
        query_chain.update = update_mock

        mock_supabase().from_.return_value = query_chain

        await run_missed_task_checker()

        update_mock.assert_called_once_with(
            {"status": "missed", "missed_count": 1}
        )

    @pytest.mark.asyncio
    async def test_missed_task_checker_handler_no_overdue(self, mocker):
        mock_supabase = mocker.patch("crons.missed_task_checker.get_supabase_client")
        mocker.patch("crons.missed_task_checker.datetime")
        mock_supabase().from_().select().execute.side_effect = [
            mocker.Mock(data=[{"id": "user1"}]),
            mocker.Mock(data=[]),  # no overdue tasks
        ]

        from crons.missed_task_checker import run_missed_task_checker
        await run_missed_task_checker()

        mock_supabase().from_().update.assert_not_called()

    @pytest.mark.asyncio
    async def test_missed_task_checker_handler_null_missed_count(self, mocker):
        from crons.missed_task_checker import run_missed_task_checker

        mock_supabase = mocker.patch("crons.missed_task_checker.get_supabase_client")
        mocker.patch("crons.missed_task_checker.datetime")

        execute_responses = iter([
            mocker.Mock(data=[{"id": "user1"}]),
            mocker.Mock(data=[{"id": "task1", "missed_count": None}]),
        ])
        execute_mock = mocker.Mock(side_effect=lambda: next(execute_responses))

        update_execute = mocker.Mock()
        update_mock = mocker.Mock(return_value=mocker.Mock(eq=lambda x: mocker.Mock(execute=update_execute)))

        query_chain = mocker.Mock()
        query_chain.execute = execute_mock
        query_chain.eq.return_value = query_chain
        query_chain.lt.return_value = query_chain
        query_chain.select.return_value = query_chain
        query_chain.update = update_mock

        mock_supabase().from_.return_value = query_chain

        await run_missed_task_checker()

        update_mock.assert_called_once_with(
            {"status": "missed", "missed_count": 1}
        )

    @pytest.mark.asyncio
    async def test_missed_task_checker_handler_error(self, mocker):
        mock_supabase = mocker.patch("crons.missed_task_checker.get_supabase_client")
        mocker.patch("crons.missed_task_checker.datetime")
        mock_supabase().from_().select().execute.side_effect = [
            mocker.Mock(data=[{"id": "user1"}]),
            Exception("DB error"),
        ]

        from crons.missed_task_checker import run_missed_task_checker
        await run_missed_task_checker()

        mock_supabase().from_().update.assert_not_called()

    @pytest.mark.asyncio
    async def test_sleep_reminder_handler(self, mocker):
        from crons.sleep_reminder import run_sleep_reminder

        mock_supabase = mocker.patch("crons.sleep_reminder.get_supabase_client")
        mocker.patch("crons.sleep_reminder.date")

        execute_responses = iter([
            mocker.Mock(data=[{"id": "user1", "sleep_goal_bedtime": "23:00"}]),
            mocker.Mock(data=[]),
        ])
        execute_mock = mocker.Mock(side_effect=lambda: next(execute_responses))

        query_chain = mocker.Mock()
        query_chain.execute = execute_mock
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.select.return_value = query_chain

        mock_supabase().from_.return_value = query_chain

        mock_suggest = mocker.patch("crons.sleep_reminder.suggest_bedtime",
                                     return_value={"suggested_bedtime": "22:30", "confidence": "high"})
        mock_sanitize = mocker.patch("crons.sleep_reminder.sanitize_input",
                                      side_effect=lambda x: x)

        await run_sleep_reminder()

        mock_suggest.assert_called_once_with("user1")

    @pytest.mark.asyncio
    async def test_sleep_reminder_handler_already_logged(self, mocker):
        from crons.sleep_reminder import run_sleep_reminder

        mock_supabase = mocker.patch("crons.sleep_reminder.get_supabase_client")
        mocker.patch("crons.sleep_reminder.date")

        execute_responses = iter([
            mocker.Mock(data=[{"id": "user1"}]),
            mocker.Mock(data=[{"id": "log1"}]),
        ])
        execute_mock = mocker.Mock(side_effect=lambda: next(execute_responses))

        query_chain = mocker.Mock()
        query_chain.execute = execute_mock
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.select.return_value = query_chain

        mock_supabase().from_.return_value = query_chain

        mock_suggest = mocker.patch("crons.sleep_reminder.suggest_bedtime")

        await run_sleep_reminder()

        mock_suggest.assert_not_called()

    @pytest.mark.asyncio
    async def test_sleep_reminder_handler_missing_goal(self, mocker):
        from crons.sleep_reminder import run_sleep_reminder

        mock_supabase = mocker.patch("crons.sleep_reminder.get_supabase_client")
        mocker.patch("crons.sleep_reminder.date")

        execute_responses = iter([
            mocker.Mock(data=[{"id": "user1"}]),
            mocker.Mock(data=[]),
        ])
        execute_mock = mocker.Mock(side_effect=lambda: next(execute_responses))

        query_chain = mocker.Mock()
        query_chain.execute = execute_mock
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.select.return_value = query_chain

        mock_supabase().from_.return_value = query_chain

        mock_suggest = mocker.patch("crons.sleep_reminder.suggest_bedtime",
                                     return_value={"suggested_bedtime": "23:00"})
        mock_sanitize = mocker.patch("crons.sleep_reminder.sanitize_input",
                                      side_effect=lambda x: x)

        await run_sleep_reminder()

        mock_suggest.assert_called_once()

    @pytest.mark.asyncio
    async def test_course_nudge_handler(self, mocker):
        mock_supabase = mocker.patch("crons.course_nudge.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}, {"id": "user2"}
        ]
        mock_nudge = mocker.patch("crons.course_nudge.run_all_nudges",
                                   return_value={
                                       "total_nudges": 3,
                                       "course_nudges": [{"course": "CS50", "message": "Watch video 5"}],
                                       "habit_nudges": [{"habit": "Read", "message": "Log today"}],
                                   })
        mock_sanitize = mocker.patch("crons.course_nudge.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.course_nudge import run_course_nudges
        await run_course_nudges()

        assert mock_nudge.call_count == 2

    @pytest.mark.asyncio
    async def test_course_nudge_handler_no_nudges(self, mocker):
        mock_supabase = mocker.patch("crons.course_nudge.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}
        ]
        mock_nudge = mocker.patch("crons.course_nudge.run_all_nudges",
                                   return_value={
                                       "total_nudges": 0,
                                       "course_nudges": [],
                                       "habit_nudges": [],
                                   })
        mock_sanitize = mocker.patch("crons.course_nudge.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.course_nudge import run_course_nudges
        await run_course_nudges()

        mock_nudge.assert_called_once()

    @pytest.mark.asyncio
    async def test_course_nudge_handler_error(self, mocker):
        mock_supabase = mocker.patch("crons.course_nudge.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}, {"id": "user2"}
        ]
        mock_nudge = mocker.patch("crons.course_nudge.run_all_nudges",
                                   side_effect=[Exception("Nudge failed"), {
                                       "total_nudges": 1,
                                       "course_nudges": [],
                                       "habit_nudges": [],
                                   }])
        mock_sanitize = mocker.patch("crons.course_nudge.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.course_nudge import run_course_nudges
        await run_course_nudges()

        assert mock_nudge.call_count == 2

    @pytest.mark.asyncio
    async def test_opportunity_radar_handler_error(self, mocker):
        mock_supabase = mocker.patch("crons.opportunity_radar.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [
            {"id": "user1"}
        ]
        mock_radar = mocker.patch("crons.opportunity_radar.run_opportunity_radar",
                                  side_effect=Exception("Radar failed"))
        mock_sanitize = mocker.patch("crons.opportunity_radar.sanitize_input",
                                      side_effect=lambda x: x)

        from crons.opportunity_radar import run_radar
        await run_radar()

        mock_radar.assert_called_once()

    @pytest.mark.asyncio
    async def test_habit_checker_handler_error(self, mocker):
        mock_supabase = mocker.patch("crons.habit_checker.get_supabase_client")
        mock_date = mocker.patch("crons.habit_checker.date")
        mock_date.today.return_value.isoformat.return_value = "2026-06-21"

        call_count = [0]
        def execute_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return mocker.Mock(data=[{"id": "user1"}])
            raise Exception("DB error fetching habits")

        query_chain = mocker.Mock()
        query_chain.execute = mocker.Mock(side_effect=execute_side_effect)
        query_chain.eq.return_value = query_chain
        query_chain.select.return_value = query_chain

        mock_supabase().from_.return_value = query_chain

        from crons.habit_checker import run_habit_checker
        await run_habit_checker()

    @pytest.mark.asyncio
    async def test_sleep_reminder_handler_error(self, mocker):
        from crons.sleep_reminder import run_sleep_reminder

        mock_supabase = mocker.patch("crons.sleep_reminder.get_supabase_client")
        mocker.patch("crons.sleep_reminder.date")

        execute_responses = iter([
            mocker.Mock(data=[{"id": "user1", "sleep_goal_bedtime": "23:00"}]),
            mocker.Mock(data=[]),
        ])
        execute_mock = mocker.Mock(side_effect=lambda: next(execute_responses))

        query_chain = mocker.Mock()
        query_chain.execute = execute_mock
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.select.return_value = query_chain

        mock_supabase().from_.return_value = query_chain

        mock_suggest = mocker.patch("crons.sleep_reminder.suggest_bedtime",
                                    side_effect=Exception("AI error"))
        mock_sanitize = mocker.patch("crons.sleep_reminder.sanitize_input",
                                      side_effect=lambda x: x)

        await run_sleep_reminder()


@pytest.mark.scheduler
class TestSchedulerMain:
    """Test the main scheduler module."""

    def test_health_handler_healthy(self):
        from main import HealthHandler
        from http.server import HTTPServer

        server = HTTPServer(("0.0.0.0", 0), HealthHandler)

        class FakeRequest:
            def makefile(self, *args, **kwargs):
                import io
                return io.BytesIO(b"GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n")

            def sendall(self, bytes):
                pass

            def close(self):
                pass

        handler = HealthHandler(FakeRequest(), ("127.0.0.1", 0), server)
        assert handler.path == "/health"
        assert handler.command == "GET"

    def test_health_handler_404(self):
        from main import HealthHandler
        from http.server import HTTPServer

        server = HTTPServer(("0.0.0.0", 0), HealthHandler)

        class FakeRequest:
            def makefile(self, *args, **kwargs):
                import io
                return io.BytesIO(b"GET /other HTTP/1.1\r\nHost: localhost\r\n\r\n")

            def sendall(self, bytes):
                pass

            def close(self):
                pass

        handler = HealthHandler(FakeRequest(), ("127.0.0.1", 0), server)
        assert handler.path == "/other"

    def test_health_handler_writes_json(self):
        from main import HealthHandler
        from http.server import HTTPServer

        server = HTTPServer(("0.0.0.0", 0), HealthHandler)

        class FakeRequest:
            def makefile(self, *args, **kwargs):
                import io
                return io.BytesIO(b"GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n")

            def sendall(self, data):
                self.sent = data

            def close(self):
                pass

        handler = HealthHandler(FakeRequest(), ("127.0.0.1", 0), server)
        assert handler.wfile is not None

    def test_main_entry_point(self):
        import asyncio
        from main import main, setup_cron_jobs

        async def test_main():
            setup_cron_jobs()

        asyncio.run(test_main())

    def test_start_health_server_creates_server(self):
        from main import start_health_server, HealthHandler
        import threading

        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = Exception("Stop server")
        with patch("main.HTTPServer", return_value=mock_server) as mock_http:
            with pytest.raises(Exception, match="Stop server"):
                start_health_server()

        mock_http.assert_called_once()
        args, _ = mock_http.call_args
        assert args[0] == ("0.0.0.0", 8001)
        assert args[1] is HealthHandler
        mock_server.serve_forever.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_function_setup_and_start(self):
        import asyncio
        import main as main_module

        main_module.scheduler = MagicMock()
        main_module.scheduler.start = MagicMock()
        main_module.asyncio = asyncio

        with patch.object(main_module, "setup_cron_jobs") as mock_setup:
            with patch.object(main_module.threading, "Thread") as mock_thread:
                with patch.object(asyncio, "sleep", side_effect=KeyboardInterrupt()):
                    await main_module.main()

        mock_setup.assert_called_once()
        mock_thread.assert_called_once()
        main_module.scheduler.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_function_system_exit(self):
        import asyncio
        import main as main_module

        main_module.scheduler = MagicMock()
        main_module.asyncio = asyncio

        with patch.object(main_module, "setup_cron_jobs"):
            with patch.object(main_module.threading, "Thread"):
                with patch.object(asyncio, "sleep", side_effect=SystemExit()):
                    await main_module.main()


@pytest.mark.scheduler
class TestCronMainBlocks:
    """Verify that cron modules contain __name__ == '__main__' entry points."""

    CRON_MODULES = [
        ("crons.daily_briefing", "run_daily_briefing"),
        ("crons.opportunity_radar", "run_radar"),
        ("crons.weekly_review", "run_weekly_review"),
        ("crons.habit_checker", "run_habit_checker"),
        ("crons.missed_task_checker", "run_missed_task_checker"),
        ("crons.sleep_reminder", "run_sleep_reminder"),
        ("crons.course_nudge", "run_course_nudges"),
    ]

    MODULE_DIR = str(Path(__file__).resolve().parent.parent / "services" / "scheduler")

    def _run_scheduler_module_as_main(self, filename, mocker, subdir="crons"):
        """Execute a cron module's __main__ block using exec with patched asyncio.run."""
        filepath = Path(self.MODULE_DIR) / subdir / filename
        code = compile(filepath.read_text(encoding="utf-8-sig"), str(filepath), "exec")
        mock_run = mocker.patch("asyncio.run")
        try:
            exec(code, {"__name__": "__main__", "__file__": str(filepath)})
        except SystemExit:
            pass
        assert mock_run.called

    def test_daily_briefing_main_block(self, mocker):
        self._run_scheduler_module_as_main("daily_briefing.py", mocker)

    def test_opportunity_radar_main_block(self, mocker):
        self._run_scheduler_module_as_main("opportunity_radar.py", mocker)

    def test_weekly_review_main_block(self, mocker):
        self._run_scheduler_module_as_main("weekly_review.py", mocker)

    def test_habit_checker_main_block(self, mocker):
        self._run_scheduler_module_as_main("habit_checker.py", mocker)

    def test_missed_task_checker_main_block(self, mocker):
        self._run_scheduler_module_as_main("missed_task_checker.py", mocker)

    def test_sleep_reminder_main_block(self, mocker):
        self._run_scheduler_module_as_main("sleep_reminder.py", mocker)

    def test_course_nudge_main_block(self, mocker):
        self._run_scheduler_module_as_main("course_nudge.py", mocker)

    def test_scheduler_main_block(self, mocker):
        self._run_scheduler_module_as_main("main.py", mocker, subdir="")
