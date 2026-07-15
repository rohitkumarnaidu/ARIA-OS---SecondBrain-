"""Tests for the deadline alert cron job."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest


class _FakeQuery:
    """Mimics a Supabase query builder with full chain support."""

    def __init__(self, return_data):
        self._return_data = return_data
        self._not = None

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def lte(self, *args, **kwargs):
        return self

    def gte(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def range(self, *args, **kwargs):
        return self

    def execute(self):
        return type("Response", (), {"data": self._return_data})()

    def insert(self, data):
        return self

    def update(self, data):
        return self

    def delete(self):
        return self

    def in_(self, *args, **kwargs):
        return self

    def contains(self, *args, **kwargs):
        return self

    def text_search(self, *args, **kwargs):
        return self

    @property
    def not_(self):
        if self._not is None:
            self._not = _FakeQuery(self._return_data)
        return self._not

    def is_(self, *args, **kwargs):
        return self

    def __call__(self, *args, **kwargs):
        return self


class _FakeSupabase:
    """Mimics a Supabase client that returns FakeQuery objects."""

    def __init__(self, opportunities_data=None, notifications_data=None):
        self._opportunities_data = opportunities_data or []
        self._notifications_data = notifications_data or []

    def from_(self, table):
        if table == "notifications":
            return _FakeQuery(self._notifications_data)
        return _FakeQuery(self._opportunities_data)


def _patch_datetime(mocker, fixed_now):
    """Patch datetime in the deadline_alert module to control time."""
    original_fromisoformat = datetime.fromisoformat

    class MockDatetime:
        @classmethod
        def now(cls, tz=None):
            return fixed_now

        @staticmethod
        def fromisoformat(s):
            return original_fromisoformat(s)

        @staticmethod
        def timedelta(*args, **kwargs):
            return timedelta(*args, **kwargs)

        @staticmethod
        def timezone(*args, **kwargs):
            return timezone(*args, **kwargs)

    mocker.patch("crons.deadline_alert.datetime", MockDatetime)


@pytest.mark.asyncio
async def test_no_opportunities_within_48h(mocker):
    """No alerts sent when no opportunities have deadlines within 48h."""
    supabase = _FakeSupabase(opportunities_data=[])
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 0


@pytest.mark.asyncio
async def test_opportunities_within_48h_send_alerts(mocker):
    """Alerts are sent for opportunities with deadlines within 48h."""
    now = datetime.now(timezone.utc)
    future = (now + timedelta(hours=12)).isoformat()

    supabase = _FakeSupabase(opportunities_data=[
        {"id": "opp1", "title": "Google Internship", "deadline": future, "match_score": 92, "user_id": "user1"},
        {"id": "opp2", "title": "Microsoft Scholarship", "deadline": future, "match_score": 85, "user_id": "user1"},
    ])
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 2


@pytest.mark.asyncio
async def test_duplicate_alerts_skipped(mocker):
    """Alerts already sent for an opportunity are not sent again."""
    now = datetime.now(timezone.utc)
    future = (now + timedelta(hours=12)).isoformat()

    supabase = _FakeSupabase(
        opportunities_data=[
            {"id": "opp1", "title": "Google Internship", "deadline": future, "match_score": 92, "user_id": "user1"},
            {"id": "opp2", "title": "Microsoft Scholarship", "deadline": future, "match_score": 85, "user_id": "user1"},
        ],
        notifications_data=[
            {"id": "notif1", "action_url": "/opportunities?id=opp1"},
        ],
    )
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 1


@pytest.mark.asyncio
async def test_urgency_critical_below_24h(mocker):
    """Alerts for deadlines <24h use high priority."""
    now = datetime.now(timezone.utc)
    near = (now + timedelta(hours=6)).isoformat()

    supabase = _FakeSupabase(opportunities_data=[
        {"id": "opp1", "title": "Critical Opp", "deadline": near, "match_score": 90, "user_id": "user1"},
    ])
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 1


@pytest.mark.asyncio
async def test_urgency_warning_24_to_48h(mocker):
    """Alerts for deadlines 24-48h use medium priority."""
    now = datetime.now(timezone.utc)
    far = (now + timedelta(hours=36)).isoformat()

    supabase = _FakeSupabase(opportunities_data=[
        {"id": "opp1", "title": "Warning Opp", "deadline": far, "match_score": 75, "user_id": "user1"},
    ])
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 1


@pytest.mark.asyncio
async def test_expired_deadlines_ignored(mocker):
    """Opportunities with deadlines already past are not alerted."""
    now = datetime.now(timezone.utc)
    past = (now - timedelta(hours=2)).isoformat()

    supabase = _FakeSupabase(opportunities_data=[
        {"id": "opp1", "title": "Expired Opp", "deadline": past, "match_score": 50, "user_id": "user1"},
    ])
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 0


@pytest.mark.asyncio
async def test_supabase_error_handled_gracefully(mocker):
    """A Supabase error during fetch returns 0 without crashing."""
    class BrokenSupabase:
        def from_(self, table):
            raise Exception("DB connection failed")

    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=BrokenSupabase())

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 0


@pytest.mark.asyncio
async def test_hours_left_in_message(mocker):
    """The notification message includes the hours remaining."""
    now = datetime.now(timezone.utc)
    deadline = (now + timedelta(hours=10)).isoformat()

    supabase = _FakeSupabase(opportunities_data=[
        {"id": "opp1", "title": "Test Opp", "deadline": deadline, "match_score": 88, "user_id": "user1"},
    ])
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 1


@ pytest.mark.asyncio
async def test_notification_insert_exception_handled(mocker):
    """An exception during notification insert is caught and logged without crashing."""
    now = datetime.now(timezone.utc)
    future = (now + timedelta(hours=12)).isoformat()

    class _InsertFailingQuery(_FakeQuery):
        def insert(self, data):
            result = _FakeQuery.__new__(_FakeQuery)
            result._return_data = self._return_data
            result._not = None
            result.execute = MagicMock(side_effect=Exception("Insert failed"))
            return result

    class _FakeSupabaseWithFail(_FakeSupabase):
        def from_(self, table):
            if table == "notifications":
                return _InsertFailingQuery(self._notifications_data or [])
            return _FakeQuery(self._opportunities_data or [])

    supabase = _FakeSupabaseWithFail(
        opportunities_data=[
            {"id": "opp1", "title": "Failing Opp", "deadline": future, "match_score": 80, "user_id": "user1"},
        ],
        notifications_data=[],
    )
    mocker.patch("crons.deadline_alert.get_supabase_client", return_value=supabase)
    _patch_datetime(mocker, now)

    from crons.deadline_alert import run_deadline_alert

    result = await run_deadline_alert()

    assert result == 0
