"""Tests for all database Pydantic schemas — creation, validation, defaults, serialization."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from database.schemas.academic import SubjectCreate, SubjectResponse, MarkCreate
from database.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate
from database.schemas.audit import AuditLogCreate, AuditLogResponse
from database.schemas.briefing import BriefingRead, BriefingListResponse, BriefingTriggerResponse
from database.schemas.chat import ChatRequest, ChatMessage, ChatResponse, ChatSessionResponse
from database.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from database.schemas.data_export import ExportRequest, ExportResponse
from database.schemas.error_response import ErrorResponse
from database.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackSummary
from database.schemas.consolidation import MemoryToCreate, MemoryToUpdate, MemoryToDiscard, ConsolidationResult
from database.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from database.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from database.schemas.idea import IdeaCreate, IdeaUpdate, IdeaResponse
from database.schemas.income import IncomeCreate, IncomeResponse
from database.schemas.memory import MemoryCreate, MemoryResponse
from database.schemas.nlp import NLPParseRequest, NLPParseResponse, NLPExecuteRequest, NLPExecuteResponse
from database.schemas.notification import NotificationResponse, NotificationRead
from database.schemas.opportunity import OpportunityCreate, OpportunityResponse
from database.schemas.prediction import (
    TimeSlot,
    SmartSlotResponse,
    BedtimePrediction,
    StreakPrediction,
    CompletionPrediction,
    HabitCompletionForecast,
    TaskCompletionForecast,
    SleepInsight,
)
from database.schemas.project import ProjectCreate, ProjectResponse
from database.schemas.prompt_history import PromptCommit, PromptHistoryResponse
from database.schemas.prompt_schema import (
    PromptMeta,
    PromptDetail,
    PromptRenderRequest,
    PromptRenderResponse,
    PromptListResponse,
)
from database.schemas.resource import ResourceCreate, ResourceResponse
from database.schemas.review import WeeklyReviewRead, WeeklyReviewListResponse
from database.schemas.roadmap import RoadmapMilestoneCreate, RoadmapMilestoneResponse
from database.schemas.sleep import SleepCreate, SleepResponse
from database.schemas.task import TaskCreate, TaskUpdate, TaskResponse, Priority, Category, TaskStatus
from database.schemas.time_entry import TimeEntryCreate, TimeEntryResponse
from database.schemas.user import UserCreate, UserUpdate, UserResponse
from database.schemas.video import VideoCreate, VideoResponse

NOW = datetime(2026, 6, 21, 12, 0, 0)


# ─────────────────────────────────────────────
# ACADEMIC
# ─────────────────────────────────────────────


class TestSubjectCreate:
    def test_valid(self):
        s = SubjectCreate(name="Data Structures")
        assert s.name == "Data Structures"
        assert s.code is None
        assert s.credits is None

    def test_with_all_fields(self):
        s = SubjectCreate(
            name="Algorithms", code="CS201", credits=4, semester="3", exam_date="2026-12-15", target_marks=90.0
        )
        assert s.code == "CS201"
        assert s.credits == 4
        assert s.target_marks == 90.0

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            SubjectCreate()

    def test_serialization(self):
        s = SubjectCreate(name="AI", target_marks=85.5)
        d = s.model_dump()
        assert d["name"] == "AI"
        assert d["target_marks"] == 85.5


class TestSubjectResponse:
    def test_valid(self):
        s = SubjectResponse(id="s1", user_id="u1", name="ML", created_at=NOW)
        assert s.id == "s1"
        assert s.name == "ML"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            SubjectResponse(user_id="u1", name="ML", created_at=NOW)

    def test_missing_user_id(self):
        with pytest.raises(ValidationError):
            SubjectResponse(id="s1", name="ML", created_at=NOW)


class TestMarkCreate:
    def test_valid(self):
        m = MarkCreate(subject_id="s1", exam_type="midterm", marks_obtained=85.0, max_marks=100.0, date="2026-06-21")
        assert m.exam_type == "midterm"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            MarkCreate()

    def test_float_precision(self):
        m = MarkCreate(subject_id="s1", exam_type="final", marks_obtained=92.5, max_marks=100.0, date="2026-06-21")
        assert m.marks_obtained == 92.5


# ─────────────────────────────────────────────
# AUDIT
# ─────────────────────────────────────────────


class TestAuditLogCreate:
    def test_valid(self):
        a = AuditLogCreate(user_id="u1", action="read", resource="tasks")
        assert a.user_id == "u1"
        assert a.action == "read"
        assert a.details is None

    def test_with_all_fields(self):
        a = AuditLogCreate(
            user_id="u1",
            action="create",
            resource="goals",
            resource_id="g1",
            details={"key": "val"},
            ip_address="127.0.0.1",
            user_agent="Mozilla",
        )
        assert a.resource_id == "g1"
        assert a.details == {"key": "val"}

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            AuditLogCreate()

    def test_serialization(self):
        a = AuditLogCreate(user_id="u1", action="delete", resource="habits")
        d = a.model_dump()
        assert d["action"] == "delete"


class TestAuditLogResponse:
    def test_valid(self):
        a = AuditLogResponse(id="a1", user_id="u1", action="update", resource="tasks", created_at=NOW)
        assert a.id == "a1"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            AuditLogResponse(user_id="u1", action="update", resource="tasks", created_at=NOW)


# ─────────────────────────────────────────────
# BRIEFING
# ─────────────────────────────────────────────


class TestBriefingRead:
    def test_valid(self):
        b = BriefingRead(id="b1", user_id="u1", date="2026-06-21", created_at=NOW)
        assert b.read is False
        assert b.title is None

    def test_with_all_fields(self):
        b = BriefingRead(
            id="b1",
            user_id="u1",
            date="2026-06-21",
            title="Morning Briefing",
            summary="Good day",
            opening="Hello",
            top_priority="Task 1",
            tasks_count=5,
            habits_streak=3,
            sleep_score=85.0,
            ai_insight="Keep going",
            productivity_tip="Focus",
            focus_area="Study",
            generated_by="ARIA",
            read=True,
            raw_json={"key": "val"},
            created_at=NOW,
        )
        assert b.read is True
        assert b.tasks_count == 5
        assert b.sleep_score == 85.0

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            BriefingRead()

    def test_default_read_false(self):
        b = BriefingRead(id="b1", user_id="u1", date="2026-06-21", created_at=NOW)
        assert b.read is False

    def test_serialization(self):
        b = BriefingRead(id="b1", user_id="u1", date="2026-06-21", created_at=NOW)
        d = b.model_dump()
        assert d["id"] == "b1"
        assert d["read"] is False


class TestBriefingListResponse:
    def test_valid(self):
        b = BriefingRead(id="b1", user_id="u1", date="2026-06-21", created_at=NOW)
        r = BriefingListResponse(data=[b], count=1)
        assert r.count == 1
        assert len(r.data) == 1

    def test_empty(self):
        r = BriefingListResponse(data=[], count=0)
        assert r.count == 0

    def test_missing_data(self):
        with pytest.raises(ValidationError):
            BriefingListResponse()


class TestBriefingTriggerResponse:
    def test_valid(self):
        r = BriefingTriggerResponse(status="ok", message="Briefing generated")
        assert r.status == "ok"

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            BriefingTriggerResponse()


# ─────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────


class TestChatRequest:
    def test_valid(self):
        c = ChatRequest(message="Hello ARIA")
        assert c.message == "Hello ARIA"
        assert c.context is None

    def test_missing_message(self):
        with pytest.raises(ValidationError):
            ChatRequest()


class TestChatMessage:
    def test_valid(self):
        c = ChatMessage(id="c1", user_id="u1", conversation_id="conv1", role="user", content="Hi", created_at=NOW)
        assert c.role == "user"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            ChatMessage()


class TestChatResponse:
    def test_valid(self):
        c = ChatResponse(response="Hello!")
        assert c.response == "Hello!"

    def test_missing_response(self):
        with pytest.raises(ValidationError):
            ChatResponse()


class TestChatSessionResponse:
    def test_valid(self):
        msg = ChatMessage(id="c1", user_id="u1", conversation_id="conv1", role="user", content="Hi", created_at=NOW)
        s = ChatSessionResponse(conversation_id="conv1", messages=[msg], ai_response="Hello!")
        assert len(s.messages) == 1

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            ChatSessionResponse()


# ─────────────────────────────────────────────
# COURSE
# ─────────────────────────────────────────────


class TestCourseCreate:
    def test_valid(self):
        c = CourseCreate(title="CS50", platform="edX")
        assert c.title == "CS50"
        assert c.total_videos == 0

    def test_default_total_videos(self):
        c = CourseCreate(title="ML Course", platform="Coursera")
        assert c.total_videos == 0

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            CourseCreate(platform="edX")

    def test_missing_platform(self):
        with pytest.raises(ValidationError):
            CourseCreate(title="CS50")


class TestCourseUpdate:
    def test_empty_update(self):
        c = CourseUpdate()
        assert c.title is None

    def test_partial_update(self):
        c = CourseUpdate(title="Updated Title")
        assert c.title == "Updated Title"
        assert c.platform is None

    def test_serialization(self):
        c = CourseUpdate(status="completed")
        d = c.model_dump()
        assert d["status"] == "completed"


class TestCourseResponse:
    def test_valid(self):
        c = CourseResponse(id="c1", user_id="u1", title="CS50", platform="edX", status="active", created_at=NOW)
        assert c.completed_videos == 0
        assert c.status == "active"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            CourseResponse(user_id="u1", title="CS50", platform="edX", status="active", created_at=NOW)

    def test_default_completed_videos(self):
        c = CourseResponse(id="c1", user_id="u1", title="CS50", platform="edX", status="active", created_at=NOW)
        assert c.completed_videos == 0


# ─────────────────────────────────────────────
# DATA EXPORT
# ─────────────────────────────────────────────


class TestExportRequest:
    def test_valid(self):
        e = ExportRequest()
        assert e.tables is None

    def test_with_tables(self):
        e = ExportRequest(tables=["tasks", "goals"])
        assert e.tables == ["tasks", "goals"]


class TestExportResponse:
    def test_valid(self):
        e = ExportResponse(
            user_id="u1", exported_at="2026-06-21T12:00:00", data={"tasks": []}, table_count=1, record_count=0
        )
        assert e.table_count == 1

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            ExportResponse()


# ─────────────────────────────────────────────
# ERROR RESPONSE
# ─────────────────────────────────────────────


class TestErrorResponse:
    def test_valid(self):
        e = ErrorResponse(detail="Not found")
        assert e.detail == "Not found"

    def test_with_all_fields(self):
        e = ErrorResponse(detail="Server error", error_code="INTERNAL", request_id="req-1", timestamp=1712345678.0)
        assert e.error_code == "INTERNAL"
        assert e.timestamp == 1712345678.0

    def test_missing_detail(self):
        with pytest.raises(ValidationError):
            ErrorResponse()

    def test_serialization(self):
        e = ErrorResponse(detail="Bad request")
        d = e.model_dump()
        assert d["detail"] == "Bad request"


# ─────────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────────


class TestFeedbackCreate:
    def test_valid(self):
        f = FeedbackCreate(source="briefing", target_id="b1", rating=5)
        assert f.rating == 5

    def test_with_all_fields(self):
        f = FeedbackCreate(source="task", target_id="t1", rating=3, comment="OK", metadata={"key": "val"})
        assert f.comment == "OK"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            FeedbackCreate()


class TestFeedbackResponse:
    def test_valid(self):
        f = FeedbackResponse(id="f1", source="briefing", target_id="b1", rating=4, created_at="2026-06-21")
        assert f.rating == 4

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            FeedbackResponse(source="briefing", target_id="b1", rating=4, created_at="2026-06-21")


class TestFeedbackSummary:
    def test_valid(self):
        f = FeedbackSummary(total=10, positive=7, negative=3, positive_rate=0.7, by_source={"briefing": 5})
        assert f.positive_rate == 0.7

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            FeedbackSummary()


# ─────────────────────────────────────────────
# GOAL
# ─────────────────────────────────────────────


class TestGoalCreate:
    def test_valid(self):
        g = GoalCreate(title="Learn React")
        assert g.roadmap_type == "career_skills"
        assert g.hours_per_day == 2.0
        assert g.days_per_week == 5.0
        assert g.intensity == "medium"

    def test_with_all_fields(self):
        g = GoalCreate(
            title="Master Python",
            description="Deep dive",
            target_date="2026-12-31",
            hours_per_day=3.0,
            days_per_week=4.0,
            intensity="high",
            category="programming",
        )
        assert g.intensity == "high"

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            GoalCreate()

    def test_defaults(self):
        g = GoalCreate(title="New Goal")
        assert g.roadmap_type == "career_skills"
        assert g.hours_per_day == 2.0

    def test_serialization(self):
        g = GoalCreate(title="Goal")
        d = g.model_dump()
        assert d["intensity"] == "medium"


class TestGoalUpdate:
    def test_empty(self):
        g = GoalUpdate()
        assert g.title is None

    def test_partial(self):
        g = GoalUpdate(status="completed", progress=100)
        assert g.progress == 100


class TestGoalResponse:
    def test_valid(self):
        g = GoalResponse(id="g1", user_id="u1", title="Goal", status="active", progress=50, created_at=NOW)
        assert g.progress == 50

    def test_missing_status(self):
        with pytest.raises(ValidationError):
            GoalResponse(id="g1", user_id="u1", title="Goal", created_at=NOW)


# ─────────────────────────────────────────────
# HABIT
# ─────────────────────────────────────────────


class TestHabitCreate:
    def test_valid(self):
        h = HabitCreate(name="Read daily")
        assert h.frequency == "daily"
        assert h.custom_days is None

    def test_with_custom_days(self):
        h = HabitCreate(name="Gym", frequency="weekly", custom_days=[0, 2, 4], time_target_minutes=30)
        assert h.custom_days == [0, 2, 4]
        assert h.time_target_minutes == 30

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            HabitCreate()

    def test_default_frequency(self):
        h = HabitCreate(name="Meditate")
        assert h.frequency == "daily"


class TestHabitUpdate:
    def test_empty(self):
        h = HabitUpdate()
        assert h.name is None

    def test_bool_field(self):
        h = HabitUpdate(is_active=False)
        assert h.is_active is False

    def test_serialization(self):
        h = HabitUpdate(name="Updated habit")
        d = h.model_dump()
        assert d["name"] == "Updated habit"


class TestHabitResponse:
    def test_valid(self):
        h = HabitResponse(id="h1", user_id="u1", name="Read", is_active=True)
        assert h.current_streak == 0
        assert h.best_streak == 0
        assert h.consistency_percentage == 0

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            HabitResponse()

    def test_defaults(self):
        h = HabitResponse(id="h1", user_id="u1", name="Read", is_active=True)
        assert h.current_streak == 0
        assert h.consistency_percentage == 0.0


# ─────────────────────────────────────────────
# IDEA
# ─────────────────────────────────────────────


class TestIdeaCreate:
    def test_valid(self):
        i = IdeaCreate(title="Startup idea")
        assert i.title == "Startup idea"

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            IdeaCreate()


class TestIdeaUpdate:
    def test_empty(self):
        i = IdeaUpdate()
        assert i.title is None

    def test_partial(self):
        i = IdeaUpdate(status="validating")
        assert i.status == "validating"


class TestIdeaResponse:
    def test_valid(self):
        i = IdeaResponse(id="i1", user_id="u1", title="Idea", status="raw", created_at=NOW)
        assert i.status == "raw"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            IdeaResponse()


# ─────────────────────────────────────────────
# INCOME
# ─────────────────────────────────────────────


class TestIncomeCreate:
    def test_valid(self):
        i = IncomeCreate(source_type="freelance", amount=500.0)
        assert i.amount == 500.0

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            IncomeCreate()

    def test_float_amount(self):
        i = IncomeCreate(source_type="salary", amount=1500.75)
        assert i.amount == 1500.75


class TestIncomeResponse:
    def test_valid(self):
        i = IncomeResponse(id="i1", user_id="u1", source_type="freelance", amount=500.0, created_at=NOW)
        assert i.effective_hourly_rate is None

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            IncomeResponse(user_id="u1", source_type="freelance", amount=500.0, created_at=NOW)


# ─────────────────────────────────────────────
# MEMORY
# ─────────────────────────────────────────────


class TestMemoryCreate:
    def test_valid(self):
        m = MemoryCreate(type="preference", key="theme", value="dark")
        assert m.importance == "medium"
        assert m.tags is None

    def test_with_all_fields(self):
        m = MemoryCreate(
            type="fact",
            key="user_name",
            value="John",
            importance="high",
            tags=["user", "personal"],
            expires_at="2026-12-31",
        )
        assert m.importance == "high"
        assert m.tags == ["user", "personal"]

    def test_default_importance(self):
        m = MemoryCreate(type="preference", key="lang", value="en")
        assert m.importance == "medium"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            MemoryCreate()

    def test_any_value_type(self):
        m = MemoryCreate(type="data", key="count", value=42)
        assert m.value == 42
        m2 = MemoryCreate(type="data", key="list", value=[1, 2, 3])
        assert m2.value == [1, 2, 3]


class TestMemoryResponse:
    def test_valid(self):
        m = MemoryResponse(
            id="m1", user_id="u1", type="fact", key="k", value="v", importance="low", created_at=NOW, updated_at=NOW
        )
        assert m.key == "k"


# ─────────────────────────────────────────────
# NLP
# ─────────────────────────────────────────────


class TestNLPParseRequest:
    def test_valid(self):
        n = NLPParseRequest(text="Create a task")
        assert n.text == "Create a task"

    def test_missing_text(self):
        with pytest.raises(ValidationError):
            NLPParseRequest()


class TestNLPParseResponse:
    def test_valid(self):
        n = NLPParseResponse(type="task", confidence=0.95, raw="Create a task")
        assert n.confidence == 0.95

    def test_float_confidence(self):
        n = NLPParseResponse(type="navigation", confidence=0.5, raw="Go to tasks")
        assert n.confidence == 0.5


class TestNLPExecuteRequest:
    def test_valid(self):
        n = NLPExecuteRequest(type="task")
        assert n.type == "task"

    def test_missing_type(self):
        with pytest.raises(ValidationError):
            NLPExecuteRequest()


class TestNLPExecuteResponse:
    def test_valid(self):
        n = NLPExecuteResponse(success=True, message="Done")
        assert n.success is True

    def test_defaults(self):
        n = NLPExecuteResponse(success=False, message="Failed")
        assert n.redirect_url is None


# ─────────────────────────────────────────────
# NOTIFICATION
# ─────────────────────────────────────────────


class TestNotificationResponse:
    def test_valid(self):
        n = NotificationResponse(
            id="n1",
            user_id="u1",
            title="Reminder",
            message="Check tasks",
            category="task",
            priority="high",
            read=False,
            created_at="2026-06-21",
        )
        assert n.priority == "high"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            NotificationResponse()


class TestNotificationRead:
    def test_valid(self):
        n = NotificationRead(id="n1")
        assert n.id == "n1"

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            NotificationRead()


# ─────────────────────────────────────────────
# OPPORTUNITY
# ─────────────────────────────────────────────


class TestOpportunityCreate:
    def test_valid(self):
        o = OpportunityCreate(title="Internship", url="https://example.com")
        assert o.opportunity_type == "internship"
        assert o.skills_required == []

    def test_defaults(self):
        o = OpportunityCreate(title="Job", url="https://example.com/job")
        assert o.opportunity_type == "internship"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            OpportunityCreate()


class TestOpportunityResponse:
    def test_valid(self):
        o = OpportunityResponse(
            id="o1", user_id="u1", title="Intern", url="https://ex.com", status="open", created_at=NOW
        )
        assert o.match_score is None

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            OpportunityResponse(user_id="u1", title="Intern", url="https://ex.com", status="open", created_at=NOW)


# ─────────────────────────────────────────────
# PREDICTION
# ─────────────────────────────────────────────


class TestTimeSlot:
    def test_valid(self):
        t = TimeSlot(hour=14, day_of_week=1, productivity_score=0.8, task_count=5, completion_rate=0.9)
        assert t.hour == 14
        assert t.productivity_score == 0.8

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            TimeSlot()


class TestSmartSlotResponse:
    def test_valid(self):
        slot = TimeSlot(hour=10, day_of_week=2, productivity_score=0.9, task_count=3, completion_rate=1.0)
        s = SmartSlotResponse(slots=[slot], best_hour=10, best_day=2)
        assert len(s.slots) == 1


class TestBedtimePrediction:
    def test_valid(self):
        b = BedtimePrediction(
            optimal_bedtime="22:00", optimal_wake="06:00", expected_score=85.0, confidence="high", based_on_sessions=30
        )
        assert b.expected_score == 85.0

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            BedtimePrediction()


class TestStreakPrediction:
    def test_valid(self):
        s = StreakPrediction(
            habit_id="h1",
            habit_name="Read",
            current_streak=5,
            risk_level="low",
            risk_probability=0.2,
            recommendation="Keep going",
        )
        assert s.risk_probability == 0.2


class TestCompletionPrediction:
    def test_valid(self):
        c = CompletionPrediction(
            task_id="t1", title="Task", probability=0.75, confidence="medium", recommendation="Focus"
        )
        assert c.probability == 0.75

    def test_with_due_date(self):
        c = CompletionPrediction(
            task_id="t1",
            title="Task",
            probability=0.75,
            confidence="medium",
            due_date="2026-07-01",
            recommendation="Prioritize",
        )
        assert c.due_date == "2026-07-01"


class TestHabitCompletionForecast:
    def test_valid(self):
        pred = StreakPrediction(
            habit_id="h1",
            habit_name="Read",
            current_streak=5,
            risk_level="low",
            risk_probability=0.2,
            recommendation="Keep going",
        )
        h = HabitCompletionForecast(total_active=10, at_risk_count=2, predictions=[pred])
        assert h.total_active == 10


class TestTaskCompletionForecast:
    def test_valid(self):
        pred = CompletionPrediction(
            task_id="t1", title="Task", probability=0.75, confidence="medium", recommendation="Focus"
        )
        t = TaskCompletionForecast(total_pending=20, high_completion=10, at_risk_count=5, predictions=[pred])
        assert t.total_pending == 20


class TestSleepInsight:
    def test_valid(self):
        s = SleepInsight(average_score=78.5, average_duration=7.5, trend="improving", recommendation="Maintain routine")
        assert s.average_score == 78.5
        assert s.bedtime_prediction is None

    def test_with_bedtime_prediction(self):
        bp = BedtimePrediction(
            optimal_bedtime="22:00", optimal_wake="06:00", expected_score=85.0, confidence="high", based_on_sessions=30
        )
        s = SleepInsight(
            average_score=78.5, average_duration=7.5, trend="stable", recommendation="Good", bedtime_prediction=bp
        )
        assert s.bedtime_prediction.optimal_bedtime == "22:00"


# ─────────────────────────────────────────────
# PROJECT
# ─────────────────────────────────────────────


class TestProjectCreate:
    def test_valid(self):
        p = ProjectCreate(title="My App")
        assert p.phase == "planning"

    def test_default_phase(self):
        p = ProjectCreate(title="Website")
        assert p.phase == "planning"

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            ProjectCreate()


class TestProjectResponse:
    def test_valid(self):
        p = ProjectResponse(id="p1", user_id="u1", title="App", created_at=NOW)
        assert p.phase == "planning"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            ProjectResponse()


# ─────────────────────────────────────────────
# PROMPT HISTORY
# ─────────────────────────────────────────────


class TestPromptCommit:
    def test_valid(self):
        p = PromptCommit(
            hash="abc123", date="2026-06-21", author="dev", message="Update prompt", additions=10, deletions=2
        )
        assert p.hash == "abc123"
        assert p.additions == 10

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            PromptCommit()


class TestPromptHistoryResponse:
    def test_valid(self):
        c = PromptCommit(hash="abc123", date="2026-06-21", author="dev", message="Update", additions=5, deletions=1)
        p = PromptHistoryResponse(name="briefing_agent", commits=[c])
        assert p.name == "briefing_agent"
        assert len(p.commits) == 1


# ─────────────────────────────────────────────
# PROMPT SCHEMA
# ─────────────────────────────────────────────


class TestPromptMeta:
    def test_valid(self):
        p = PromptMeta(
            name="test",
            category="agents",
            file_path="prompts/agents/test.md",
            frontmatter={"version": "1.0"},
            body_length=100,
            word_count=20,
        )
        assert p.word_count == 20


class TestPromptDetail:
    def test_valid(self):
        p = PromptDetail(
            name="test",
            category="agents",
            file_path="prompts/agents/test.md",
            frontmatter={"version": "1.0"},
            body="# Hello",
            body_length=7,
            word_count=1,
        )
        assert p.body == "# Hello"


class TestPromptRenderRequest:
    def test_valid(self):
        p = PromptRenderRequest()
        assert p.variables == {}

    def test_with_variables(self):
        p = PromptRenderRequest(variables={"name": "John"})
        assert p.variables["name"] == "John"


class TestPromptRenderResponse:
    def test_valid(self):
        p = PromptRenderResponse(name="test", rendered="# Rendered", frontmatter={"version": "1.0"})
        assert p.name == "test"


class TestPromptListResponse:
    def test_valid(self):
        meta = PromptMeta(
            name="test", category="agents", file_path="test.md", frontmatter={}, body_length=10, word_count=2
        )
        p = PromptListResponse(total=1, prompts=[meta])
        assert p.total == 1


# ─────────────────────────────────────────────
# RESOURCE
# ─────────────────────────────────────────────


class TestResourceCreate:
    def test_valid(self):
        r = ResourceCreate(title="Python Docs", url="https://docs.python.org")
        assert r.resource_type == "article"
        assert r.tags == []

    def test_default_resource_type(self):
        r = ResourceCreate(title="Tutorial", url="https://example.com")
        assert r.resource_type == "article"


class TestResourceResponse:
    def test_valid(self):
        r = ResourceResponse(id="r1", user_id="u1", title="Docs", url="https://example.com", created_at=NOW)
        assert r.is_archived is False

    def test_default_is_archived(self):
        r = ResourceResponse(id="r1", user_id="u1", title="Docs", url="https://example.com", created_at=NOW)
        assert r.is_archived is False


# ─────────────────────────────────────────────
# REVIEW (Weekly Review)
# ─────────────────────────────────────────────


class TestWeeklyReviewRead:
    def test_valid(self):
        r = WeeklyReviewRead(id="r1", user_id="u1", week_start="2026-06-15", week_end="2026-06-21", created_at=NOW)
        assert r.summary is None

    def test_with_all_fields(self):
        r = WeeklyReviewRead(
            id="r1",
            user_id="u1",
            week_start="2026-06-15",
            week_end="2026-06-21",
            summary="Good week",
            tasks_completed=12,
            tasks_added=5,
            habits_consistency=0.8,
            focus_hours=25.0,
            highlights=["Task A"],
            challenges=["Task B"],
            next_week_focus=["Task C"],
            ai_insights="Keep it up",
            mood_trend="positive",
            generated_by="ARIA",
            created_at=NOW,
        )
        assert r.tasks_completed == 12
        assert r.habits_consistency == 0.8

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            WeeklyReviewRead()

    def test_list_fields(self):
        r = WeeklyReviewRead(
            id="r1",
            user_id="u1",
            week_start="2026-06-15",
            week_end="2026-06-21",
            highlights=["A", "B"],
            challenges=["C"],
            next_week_focus=["D"],
            created_at=NOW,
        )
        assert r.highlights == ["A", "B"]
        assert r.challenges == ["C"]


class TestWeeklyReviewListResponse:
    def test_valid(self):
        r = WeeklyReviewRead(id="r1", user_id="u1", week_start="2026-06-15", week_end="2026-06-21", created_at=NOW)
        resp = WeeklyReviewListResponse(data=[r], count=1)
        assert resp.count == 1


# ─────────────────────────────────────────────
# ROADMAP
# ─────────────────────────────────────────────


class TestRoadmapMilestoneCreate:
    def test_valid(self):
        r = RoadmapMilestoneCreate(skill="Python", category="Programming")
        assert r.progress == 0.0
        assert r.status == "not_started"
        assert r.is_recommended is False

    def test_defaults(self):
        r = RoadmapMilestoneCreate(skill="Docker", category="DevOps")
        assert r.progress == 0.0
        assert r.status == "not_started"

    def test_with_all_fields(self):
        r = RoadmapMilestoneCreate(
            skill="Kubernetes",
            category="DevOps",
            target_date="2026-12-31",
            progress=50.0,
            status="in_progress",
            is_recommended=True,
        )
        assert r.progress == 50.0
        assert r.is_recommended is True


class TestRoadmapMilestoneResponse:
    def test_valid(self):
        r = RoadmapMilestoneResponse(
            id="r1",
            user_id="u1",
            skill="Python",
            category="Programming",
            progress=25.0,
            status="in_progress",
            created_at=NOW,
            updated_at=NOW,
        )
        assert r.is_recommended is False

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            RoadmapMilestoneResponse()


# ─────────────────────────────────────────────
# SLEEP
# ─────────────────────────────────────────────


class TestSleepCreate:
    def test_valid(self):
        s = SleepCreate(bedtime="22:00", wake_time="06:00", quality_rating=4)
        assert s.bedtime == "22:00"
        assert s.quality_rating == 4

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            SleepCreate()


class TestSleepResponse:
    def test_valid(self):
        s = SleepResponse(id="s1", user_id="u1", bedtime="22:00", wake_time="06:00", quality_rating=4, created_at=NOW)
        assert s.duration_hours == 0.0
        assert s.sleep_score == 0
        assert s.sleep_debt == 0.0

    def test_defaults(self):
        s = SleepResponse(id="s1", user_id="u1", bedtime="22:00", wake_time="06:00", quality_rating=4, created_at=NOW)
        assert s.duration_hours == 0.0
        assert s.sleep_score == 0


# ─────────────────────────────────────────────
# TASK (with Enums)
# ─────────────────────────────────────────────


class TestTaskCreate:
    def test_valid(self):
        t = TaskCreate(title="Complete assignment")
        assert t.title == "Complete assignment"
        assert t.priority == Priority.medium
        assert t.category == Category.personal
        assert t.is_recurring is False

    def test_with_enums(self):
        t = TaskCreate(title="Study", priority=Priority.high, category=Category.study)
        assert t.priority == Priority.high
        assert t.category == Category.study

    def test_with_due_date(self):
        t = TaskCreate(title="Task", due_date=NOW)
        assert t.due_date == NOW

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            TaskCreate()

    def test_defaults(self):
        t = TaskCreate(title="Default task")
        assert t.priority == Priority.medium
        assert t.category == Category.personal
        assert t.is_recurring is False
        assert t.estimated_minutes is None

    def test_serialization(self):
        t = TaskCreate(title="Task")
        d = t.model_dump()
        assert d["title"] == "Task"
        assert d["priority"] == "medium"
        assert d["category"] == "personal"

    def test_recurring_frequency(self):
        t = TaskCreate(title="Weekly review", is_recurring=True, recurring_frequency="weekly")
        assert t.recurring_frequency == "weekly"

    def test_invalid_priority_raises(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", priority="invalid")


class TestTaskUpdate:
    def test_empty(self):
        t = TaskUpdate()
        assert t.title is None

    def test_partial(self):
        t = TaskUpdate(status=TaskStatus.completed, completed_at=NOW)
        assert t.status == TaskStatus.completed
        assert t.completed_at == NOW

    def test_enum_update(self):
        t = TaskUpdate(priority=Priority.urgent)
        assert t.priority == Priority.urgent

    def test_bool_update(self):
        t = TaskUpdate(is_recurring=True)
        assert t.is_recurring is True


class TestTaskResponse:
    def test_valid(self):
        t = TaskResponse(
            id="t1",
            user_id="u1",
            title="Task",
            status=TaskStatus.pending,
            completed_at=None,
            missed_count=0,
            created_at=NOW,
            updated_at=NOW,
        )
        assert t.status == TaskStatus.pending
        assert t.missed_count == 0
        assert t.completed_at is None

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            TaskResponse()

    def test_default_missed_count(self):
        with pytest.raises(ValidationError):
            TaskResponse(id="t1", user_id="u1", title="Task", status=TaskStatus.pending, created_at=NOW, updated_at=NOW)

    def test_completed_at(self):
        t = TaskResponse(
            id="t1",
            user_id="u1",
            title="Task",
            status=TaskStatus.completed,
            completed_at=NOW,
            missed_count=0,
            created_at=NOW,
            updated_at=NOW,
        )
        assert t.completed_at == NOW

    def test_serialization(self):
        t = TaskResponse(
            id="t1",
            user_id="u1",
            title="Task",
            status=TaskStatus.pending,
            completed_at=None,
            missed_count=0,
            created_at=NOW,
            updated_at=NOW,
        )
        d = t.model_dump()
        assert d["status"] == "pending"

    def test_goal_id(self):
        t = TaskCreate(title="Task", goal_id="g1")
        assert t.goal_id == "g1"


# ─────────────────────────────────────────────
# TIME ENTRY
# ─────────────────────────────────────────────


class TestTimeEntryCreate:
    def test_valid(self):
        t = TimeEntryCreate(start_time=NOW)
        assert t.category == "work"
        assert t.task_id is None

    def test_default_category(self):
        t = TimeEntryCreate(start_time=NOW)
        assert t.category == "work"

    def test_with_all_fields(self):
        t = TimeEntryCreate(
            task_id="t1",
            project_id="p1",
            start_time=NOW,
            end_time=NOW,
            duration_minutes=60,
            description="Worked on feature",
            category="development",
        )
        assert t.duration_minutes == 60
        assert t.category == "development"

    def test_missing_start_time(self):
        with pytest.raises(ValidationError):
            TimeEntryCreate()

    def test_serialization(self):
        t = TimeEntryCreate(start_time=NOW)
        d = t.model_dump()
        assert d["category"] == "work"


class TestTimeEntryResponse:
    def test_valid(self):
        t = TimeEntryResponse(
            id="t1",
            user_id="u1",
            task_id=None,
            project_id=None,
            start_time="2026-06-21T12:00:00",
            end_time=None,
            duration_minutes=None,
            description=None,
            category="work",
            created_at=NOW,
        )
        assert t.task_id is None

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            TimeEntryResponse()


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────


class TestUserCreate:
    def test_valid(self):
        u = UserCreate(email="test@example.com")
        assert u.email == "test@example.com"
        assert u.skills == []

    def test_with_all_fields(self):
        u = UserCreate(
            email="user@example.com",
            name="John",
            avatar_url="https://av.com/a.jpg",
            college="MIT",
            year=3,
            skills=["Python", "React"],
            bio="Developer",
        )
        assert u.year == 3
        assert u.skills == ["Python", "React"]

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            UserCreate()

    def test_default_skills(self):
        u = UserCreate(email="a@b.com")
        assert u.skills == []

    def test_serialization(self):
        u = UserCreate(email="a@b.com")
        d = u.model_dump()
        assert d["email"] == "a@b.com"


class TestUserUpdate:
    def test_empty(self):
        u = UserUpdate()
        assert u.name is None

    def test_dict_fields(self):
        u = UserUpdate(daily_routine={"wake": "06:00"}, opportunity_preferences={"remote": True})
        assert u.daily_routine["wake"] == "06:00"
        assert u.opportunity_preferences["remote"] is True


class TestUserResponse:
    def test_valid(self):
        u = UserResponse(id="u1", email="test@example.com", created_at=NOW, updated_at=NOW)
        assert u.email == "test@example.com"
        assert u.skills == []

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            UserResponse(email="test@example.com", created_at=NOW, updated_at=NOW)

    def test_default_skills(self):
        u = UserResponse(id="u1", email="test@example.com", created_at=NOW, updated_at=NOW)
        assert u.skills == []


# ─────────────────────────────────────────────
# VIDEO
# ─────────────────────────────────────────────


class TestVideoCreate:
    def test_valid(self):
        v = VideoCreate(url="https://youtube.com/watch?v=abc", title="Tutorial")
        assert v.status == "saved"

    def test_default_status(self):
        v = VideoCreate(url="https://example.com/video", title="How-to")
        assert v.status == "saved"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            VideoCreate()


class TestVideoResponse:
    def test_valid(self):
        v = VideoResponse(
            id="v1",
            user_id="u1",
            url="https://youtube.com/watch?v=abc",
            title="Tutorial",
            status="saved",
            created_at=NOW,
        )
        assert v.status == "saved"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            VideoResponse()


class TestMemoryToCreate:
    def test_valid(self):
        m = MemoryToCreate(type="preference", key="theme", value="dark")
        assert m.type == "preference"
        assert m.key == "theme"
        assert m.value == "dark"
        assert m.importance == "medium"
        assert m.tags is None

    def test_with_tags(self):
        m = MemoryToCreate(type="fact", key="name", value="Alice", importance="high", tags=["user", "personal"])
        assert m.tags == ["user", "personal"]
        assert m.importance == "high"


class TestMemoryToUpdate:
    def test_valid(self):
        m = MemoryToUpdate(id="mem-1", updates={"value": "new-value"})
        assert m.id == "mem-1"


class TestMemoryToDiscard:
    def test_valid(self):
        m = MemoryToDiscard(id="mem-1", reason="duplicate")
        assert m.id == "mem-1"
        assert m.reason == "duplicate"


class TestConsolidationResult:
    def test_valid(self):
        r = ConsolidationResult(
            consolidation_type="daily",
            memories_created=3,
            memories_updated=1,
            memories_discarded=0,
            patterns_detected=1,
            summary="Consolidated 3 memories",
        )
        assert r.consolidation_type == "daily"
        assert r.memories_created == 3

    def test_with_details(self):
        r = ConsolidationResult(
            consolidation_type="daily",
            memories_created=1,
            memories_updated=0,
            memories_discarded=0,
            patterns_detected=0,
            summary="Done",
            details={"created": ["mem-1"]},
        )
        assert r.details == {"created": ["mem-1"]}

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            ConsolidationResult()


# ─────────────────────────────────────────────
# API KEY
# ─────────────────────────────────────────────


class TestApiKeyTier:
    def test_constants(self):
        from database.schemas.api_key import ApiKeyTier

        assert ApiKeyTier.FREE == "free"
        assert ApiKeyTier.PRO == "pro"
        assert ApiKeyTier.ENTERPRISE == "enterprise"
        assert ApiKeyTier.INTERNAL == "internal"


class TestTierLimits:
    def test_all_tiers_present(self):
        from database.schemas.api_key import TIER_LIMITS, ApiKeyTier

        assert ApiKeyTier.FREE in TIER_LIMITS
        assert ApiKeyTier.PRO in TIER_LIMITS
        assert ApiKeyTier.ENTERPRISE in TIER_LIMITS
        assert ApiKeyTier.INTERNAL in TIER_LIMITS

    def test_free_tier_limits(self):
        from database.schemas.api_key import TIER_LIMITS

        assert TIER_LIMITS["free"]["max_requests"] == 10
        assert TIER_LIMITS["free"]["window_seconds"] == 60
        assert TIER_LIMITS["free"]["concurrent"] == 1

    def test_pro_tier_limits(self):
        from database.schemas.api_key import TIER_LIMITS

        assert TIER_LIMITS["pro"]["max_requests"] == 100
        assert TIER_LIMITS["pro"]["concurrent"] == 10

    def test_enterprise_tier_limits(self):
        from database.schemas.api_key import TIER_LIMITS

        assert TIER_LIMITS["enterprise"]["max_requests"] == 1000
        assert TIER_LIMITS["enterprise"]["concurrent"] == 100

    def test_internal_tier_limits(self):
        from database.schemas.api_key import TIER_LIMITS

        assert TIER_LIMITS["internal"]["max_requests"] == 10000
        assert TIER_LIMITS["internal"]["concurrent"] == 500

    def test_all_tiers_have_required_keys(self):
        from database.schemas.api_key import TIER_LIMITS

        for key, limits in TIER_LIMITS.items():
            assert "max_requests" in limits
            assert "window_seconds" in limits
            assert "concurrent" in limits
            assert isinstance(limits["max_requests"], int)
            assert isinstance(limits["window_seconds"], int)
            assert isinstance(limits["concurrent"], int)


class TestApiKeyCreate:
    def test_valid(self):
        k = ApiKeyCreate(name="My API Key")
        assert k.name == "My API Key"
        assert k.tier == "free"
        assert k.expires_at is None

    def test_with_all_fields(self):
        k = ApiKeyCreate(name="Pro Key", tier="pro", expires_at=NOW)
        assert k.tier == "pro"
        assert k.expires_at == NOW

    def test_enterprise_tier(self):
        k = ApiKeyCreate(name="Enterprise Key", tier="enterprise")
        assert k.tier == "enterprise"

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            ApiKeyCreate()

    def test_default_tier(self):
        k = ApiKeyCreate(name="Free Key")
        assert k.tier == "free"

    def test_serialization(self):
        k = ApiKeyCreate(name="Test", tier="free")
        d = k.model_dump()
        assert d["name"] == "Test"
        assert d["tier"] == "free"
        assert d["expires_at"] is None


class TestApiKeyResponse:
    def test_valid(self):
        k = ApiKeyResponse(
            id="ak-1",
            name="My Key",
            key_prefix="sb_",
            tier="pro",
            is_active=True,
            expires_at=None,
            last_used_at=None,
            created_at=NOW,
        )
        assert k.id == "ak-1"
        assert k.name == "My Key"
        assert k.key_prefix == "sb_"
        assert k.tier == "pro"
        assert k.is_active is True
        assert k.expires_at is None
        assert k.last_used_at is None

    def test_with_all_fields(self):
        k = ApiKeyResponse(
            id="ak-2",
            name="Full Key",
            key_prefix="sb_",
            tier="enterprise",
            is_active=False,
            expires_at=NOW,
            last_used_at=NOW,
            created_at=NOW,
        )
        assert k.is_active is False
        assert k.expires_at == NOW
        assert k.last_used_at == NOW

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            ApiKeyResponse(name="Key", key_prefix="sb_", tier="free", is_active=True, expires_at=None, last_used_at=None, created_at=NOW)

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            ApiKeyResponse(id="ak-1", key_prefix="sb_", tier="free", is_active=True, expires_at=None, last_used_at=None, created_at=NOW)

    def test_missing_key_prefix(self):
        with pytest.raises(ValidationError):
            ApiKeyResponse(id="ak-1", name="Key", tier="free", is_active=True, expires_at=None, last_used_at=None, created_at=NOW)

    def test_missing_is_active(self):
        with pytest.raises(ValidationError):
            ApiKeyResponse(id="ak-1", name="Key", key_prefix="sb_", tier="free", expires_at=None, last_used_at=None, created_at=NOW)

    def test_serialization(self):
        k = ApiKeyResponse(
            id="ak-1",
            name="Key",
            key_prefix="sb_",
            tier="free",
            is_active=True,
            expires_at=None,
            last_used_at=None,
            created_at=NOW,
        )
        d = k.model_dump()
        assert d["id"] == "ak-1"
        assert d["is_active"] is True


class TestApiKeyUpdate:
    def test_empty(self):
        k = ApiKeyUpdate()
        assert k.name is None
        assert k.is_active is None
        assert k.tier is None

    def test_partial_name(self):
        k = ApiKeyUpdate(name="Renamed Key")
        assert k.name == "Renamed Key"
        assert k.is_active is None

    def test_partial_deactivate(self):
        k = ApiKeyUpdate(is_active=False)
        assert k.is_active is False
        assert k.name is None

    def test_partial_tier(self):
        k = ApiKeyUpdate(tier="enterprise")
        assert k.tier == "enterprise"

    def test_all_fields(self):
        k = ApiKeyUpdate(name="Updated", is_active=False, tier="pro")
        assert k.name == "Updated"
        assert k.is_active is False
        assert k.tier == "pro"

    def test_serialization(self):
        k = ApiKeyUpdate(name="Key", is_active=False)
        d = k.model_dump()
        assert d["name"] == "Key"
        assert d["is_active"] is False
        assert d["tier"] is None
