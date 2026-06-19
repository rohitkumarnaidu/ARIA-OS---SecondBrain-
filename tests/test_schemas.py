"""Comprehensive tests for all Pydantic database schemas (13 modules)."""

import pytest
from datetime import datetime

# ─── Chat ───────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestChatSchemas:
    """ChatMessage, ChatRequest, ChatResponse, ChatSessionResponse"""

    def test_chat_request_requires_message(self):
        from database.schemas.chat import ChatRequest

        req = ChatRequest(message="Hello ARIA")
        assert req.message == "Hello ARIA"
        assert req.context is None
        assert req.conversation_id is None

    def test_chat_request_with_optionals(self):
        from database.schemas.chat import ChatRequest

        req = ChatRequest(message="Hi", context="user ctx", conversation_id="conv-1")
        assert req.message == "Hi"
        assert req.context == "user ctx"
        assert req.conversation_id == "conv-1"

    def test_chat_request_missing_message_raises(self):
        from database.schemas.chat import ChatRequest

        with pytest.raises(ValueError):
            ChatRequest()

    def test_chat_message_all_required(self):
        from database.schemas.chat import ChatMessage

        msg = ChatMessage(
            id="m-1",
            user_id="u-1",
            conversation_id="c-1",
            role="user",
            content="Hello",
            created_at="2026-06-17T00:00:00Z",
        )
        assert msg.id == "m-1"
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_chat_message_missing_field_raises(self):
        from database.schemas.chat import ChatMessage

        with pytest.raises(ValueError):
            ChatMessage(id="m-1", user_id="u-1", role="user", content="Hi")

    def test_chat_response_simple(self):
        from database.schemas.chat import ChatResponse

        resp = ChatResponse(response="Hello!", action_taken="none")
        assert resp.response == "Hello!"
        assert resp.action_taken == "none"

    def test_chat_response_default_action(self):
        from database.schemas.chat import ChatResponse

        resp = ChatResponse(response="Hi")
        assert resp.response == "Hi"
        assert resp.action_taken is None

    def test_chat_session_response_contains_list(self):
        from database.schemas.chat import ChatMessage, ChatSessionResponse

        msgs = [
            ChatMessage(id="m-1", user_id="u-1", conversation_id="c-1", role="user", content="Hi", created_at="2026-06-01T12:00:00Z"),
        ]
        resp = ChatSessionResponse(conversation_id="c-1", messages=msgs, ai_response="Hello!")
        assert resp.conversation_id == "c-1"
        assert len(resp.messages) == 1
        assert resp.ai_response == "Hello!"

    def test_chat_session_response_from_dict(self):
        from database.schemas.chat import ChatSessionResponse

        data = {
            "conversation_id": "c-1",
            "messages": [
                {
                    "id": "m-1",
                    "user_id": "u-1",
                    "conversation_id": "c-1",
                    "role": "user",
                    "content": "Hi",
                    "created_at": "2026-06-01T12:00:00Z",
                },
            ],
            "ai_response": "Hello!",
        }
        resp = ChatSessionResponse(**data)
        assert resp.conversation_id == "c-1"
        assert resp.messages[0].role == "user"

    def test_chat_session_response_missing_field_raises(self):
        from database.schemas.chat import ChatSessionResponse

        with pytest.raises(ValueError):
            ChatSessionResponse(conversation_id="c-1")


# ─── Course ─────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestCourseSchemas:
    """CourseCreate, CourseUpdate, CourseResponse"""

    def test_course_create_requires_title_and_platform(self):
        from database.schemas.course import CourseCreate

        course = CourseCreate(title="Python 101", platform="Udemy")
        assert course.title == "Python 101"
        assert course.total_videos == 0
        assert course.platform == "Udemy"

    def test_course_create_with_optionals(self):
        from database.schemas.course import CourseCreate

        course = CourseCreate(
            title="ML Specialization",
            platform="Coursera",
            url="https://coursera.org/ml",
            total_videos=120,
            deadline="2026-12-31",
            why_enrolled="Career growth",
        )
        assert course.platform == "Coursera"
        assert course.total_videos == 120

    def test_course_create_defaults(self):
        from database.schemas.course import CourseCreate

        course = CourseCreate(title="Test", platform="YouTube")
        assert course.total_videos == 0

    def test_course_create_missing_title_raises(self):
        from database.schemas.course import CourseCreate

        with pytest.raises(ValueError):
            CourseCreate()

    def test_course_update_all_optional(self):
        from database.schemas.course import CourseUpdate

        update = CourseUpdate(completed_videos=50, status="completed")
        assert update.completed_videos == 50
        assert update.status == "completed"
        assert update.title is None

    def test_course_update_empty(self):
        from database.schemas.course import CourseUpdate

        update = CourseUpdate()
        assert update.title is None
        assert update.completed_videos is None

    def test_course_response_from_dict(self):
        from database.schemas.course import CourseResponse

        data = {
            "id": "course-1",
            "user_id": "u-1",
            "status": "active",
            "title": "Python",
            "platform": "Udemy",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = CourseResponse(**data)
        assert resp.id == "course-1"
        assert resp.status == "active"
        assert resp.completed_videos == 0

    def test_course_response_all_fields(self):
        from database.schemas.course import CourseResponse

        data = {
            "id": "c-1",
            "user_id": "u-1",
            "status": "completed",
            "title": "Advanced ML",
            "platform": "Udemy",
            "url": "https://udemy.com/ml",
            "total_videos": 80,
            "completed_videos": 80,
            "deadline": "2026-06-01",
            "why_enrolled": "Upskill",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = CourseResponse(**data)
        assert resp.total_videos == 80
        assert resp.completed_videos == 80
        assert resp.why_enrolled == "Upskill"

    def test_course_response_missing_required_raises(self):
        from database.schemas.course import CourseResponse

        with pytest.raises(ValueError):
            CourseResponse(id="c-1", status="active", title="T")

    def test_course_create_invalid_type_for_int(self):
        from database.schemas.course import CourseCreate

        with pytest.raises(ValueError):
            CourseCreate(title="T", total_videos="not-a-number")


# ─── Goal ───────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestGoalSchemas:
    """GoalCreate, GoalUpdate, GoalResponse"""

    def test_goal_create_requires_title(self):
        from database.schemas.goal import GoalCreate

        g = GoalCreate(title="Learn Rust")
        assert g.title == "Learn Rust"
        assert g.roadmap_type == "career_skills"
        assert g.hours_per_day == 2.0
        assert g.days_per_week == 5.0
        assert g.intensity == "medium"
        assert g.category is None

    def test_goal_create_with_optionals(self):
        from database.schemas.goal import GoalCreate

        g = GoalCreate(
            title="Master React",
            description="Become proficient",
            roadmap_type="web_dev",
            target_date="2026-12-31",
            hours_per_day=3.0,
            days_per_week=4.0,
            intensity="high",
            category="learning",
        )
        assert g.description == "Become proficient"
        assert g.target_date == "2026-12-31"
        assert g.intensity == "high"
        assert g.category == "learning"

    def test_goal_create_defaults(self):
        from database.schemas.goal import GoalCreate

        g = GoalCreate(title="T")
        assert g.roadmap_type == "career_skills"
        assert g.hours_per_day == 2.0
        assert g.days_per_week == 5.0
        assert g.intensity == "medium"

    def test_goal_update_partial(self):
        from database.schemas.goal import GoalUpdate

        u = GoalUpdate(status="completed", progress=100)
        assert u.status == "completed"
        assert u.progress == 100
        assert u.title is None

    def test_goal_response_from_dict(self):
        from database.schemas.goal import GoalResponse

        data = {
            "id": "g-1",
            "user_id": "u-1",
            "status": "active",
            "progress": 50,
            "title": "Learn Go",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = GoalResponse(**data)
        assert resp.id == "g-1"
        assert resp.progress == 50
        assert resp.roadmap_type == "career_skills"

    def test_goal_response_missing_required_raises(self):
        from database.schemas.goal import GoalResponse

        with pytest.raises(ValueError):
            GoalResponse(id="g-1", user_id="u-1")

    def test_goal_create_float_defaults(self):
        from database.schemas.goal import GoalCreate

        g = GoalCreate(title="T")
        assert isinstance(g.hours_per_day, float)
        assert isinstance(g.days_per_week, float)


# ─── Habit ──────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestHabitSchemas:
    """HabitCreate, HabitUpdate, HabitResponse"""

    def test_habit_create_requires_name(self):
        from database.schemas.habit import HabitCreate

        h = HabitCreate(name="Meditate")
        assert h.name == "Meditate"
        assert h.frequency == "daily"

    def test_habit_create_with_optionals(self):
        from database.schemas.habit import HabitCreate

        h = HabitCreate(
            name="Read",
            frequency="weekly",
            custom_days=[0, 2, 4],
            time_target_minutes=20,
        )
        assert h.frequency == "weekly"
        assert h.custom_days == [0, 2, 4]
        assert h.time_target_minutes == 20

    def test_habit_update_with_is_active(self):
        from database.schemas.habit import HabitUpdate

        u = HabitUpdate(is_active=False, name="Read Books")
        assert u.is_active is False
        assert u.name == "Read Books"

    def test_habit_response_from_dict(self):
        from database.schemas.habit import HabitResponse

        data = {
            "id": "h-1",
            "user_id": "u-1",
            "is_active": True,
            "name": "Exercise",
        }
        resp = HabitResponse(**data)
        assert resp.is_active is True
        assert resp.name == "Exercise"
        assert resp.frequency == "daily"

    def test_habit_response_missing_user_id_raises(self):
        from database.schemas.habit import HabitResponse

        with pytest.raises(ValueError):
            HabitResponse(id="h-1", is_active=True, name="T")


# ─── Idea ───────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestIdeaSchemas:
    """IdeaCreate, IdeaUpdate, IdeaResponse"""

    def test_idea_create_requires_title(self):
        from database.schemas.idea import IdeaCreate

        idea = IdeaCreate(title="Build an app")
        assert idea.title == "Build an app"

    def test_idea_create_with_optionals(self):
        from database.schemas.idea import IdeaCreate

        idea = IdeaCreate(
            title="Startup idea",
            description="AI for X",
        )
        assert idea.description == "AI for X"

    def test_idea_update_with_status(self):
        from database.schemas.idea import IdeaUpdate

        u = IdeaUpdate(status="validating", market_research="Growing market")
        assert u.status == "validating"
        assert u.market_research == "Growing market"

    def test_idea_response_from_dict(self):
        from database.schemas.idea import IdeaResponse

        data = {
            "id": "i-1",
            "user_id": "u-1",
            "status": "raw",
            "title": "New idea",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = IdeaResponse(**data)
        assert resp.status == "raw"

    def test_idea_response_missing_required_raises(self):
        from database.schemas.idea import IdeaResponse

        with pytest.raises(ValueError):
            IdeaResponse(id="i-1")


# ─── Income ─────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestIncomeSchemas:
    """IncomeCreate, IncomeUpdate, IncomeResponse"""

    def test_income_create_requires_source_type_and_amount(self):
        from database.schemas.income import IncomeCreate

        inc = IncomeCreate(source_type="Freelance", amount=500.0)
        assert inc.source_type == "Freelance"
        assert inc.amount == 500.0
        assert inc.hours_spent is None

    def test_income_create_missing_amount_raises(self):
        from database.schemas.income import IncomeCreate

        with pytest.raises(ValueError):
            IncomeCreate(source_type="Work")

    def test_income_create_missing_source_type_raises(self):
        from database.schemas.income import IncomeCreate

        with pytest.raises(ValueError):
            IncomeCreate(amount=100.0)

    def test_income_create_with_optionals(self):
        from database.schemas.income import IncomeCreate

        inc = IncomeCreate(
            source_type="Salary",
            amount=3000.0,
            platform="Upwork",
            date="2026-06-01",
            description="Monthly",
            hours_spent=40.0,
        )
        assert inc.platform == "Upwork"
        assert inc.hours_spent == 40.0

    def test_income_update_partial(self):
        from database.schemas.income import IncomeUpdate

        u = IncomeUpdate(amount=600.0)
        assert u.amount == 600.0
        assert u.source_type is None

    def test_income_response_from_dict(self):
        from database.schemas.income import IncomeResponse

        data = {
            "id": "inc-1",
            "user_id": "u-1",
            "source_type": "Bonus",
            "amount": 1000.0,
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = IncomeResponse(**data)
        assert resp.amount == 1000.0
        assert resp.source_type == "Bonus"

    def test_income_response_missing_amount_raises(self):
        from database.schemas.income import IncomeResponse

        with pytest.raises(ValueError):
            IncomeResponse(id="inc-1", user_id="u-1", source_type="T")


# ─── Opportunity ────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestOpportunitySchemas:
    """OpportunityCreate, OpportunityUpdate, OpportunityResponse"""

    def test_opportunity_create_requires_title_and_url(self):
        from database.schemas.opportunity import OpportunityCreate

        opp = OpportunityCreate(title="Google Intern", url="https://careers.google.com")
        assert opp.title == "Google Intern"
        assert opp.url == "https://careers.google.com"
        assert opp.opportunity_type == "internship"

    def test_opportunity_create_missing_url_raises(self):
        from database.schemas.opportunity import OpportunityCreate

        with pytest.raises(ValueError):
            OpportunityCreate(title="Job")

    def test_opportunity_create_with_optionals(self):
        from database.schemas.opportunity import OpportunityCreate

        opp = OpportunityCreate(
            title="Microsoft Intern",
            url="https://microsoft.com",
            opportunity_type="internship",
            company="Microsoft",
            description="SWE intern",
            skills_required=["Python", "Azure"],
            deadline="2026-09-01",
        )
        assert opp.company == "Microsoft"
        assert opp.skills_required == ["Python", "Azure"]

    def test_opportunity_update_with_status(self):
        from database.schemas.opportunity import OpportunityUpdate

        u = OpportunityUpdate(status="applied", deadline="2026-10-01")
        assert u.status == "applied"
        assert u.deadline == "2026-10-01"

    def test_opportunity_response_from_dict(self):
        from database.schemas.opportunity import OpportunityResponse

        data = {
            "id": "opp-1",
            "user_id": "u-1",
            "status": "saved",
            "title": "Startup Job",
            "url": "https://startup.com",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = OpportunityResponse(**data)
        assert resp.status == "saved"
        assert resp.opportunity_type == "internship"
        assert resp.match_score is None

    def test_opportunity_response_with_match_score(self):
        from database.schemas.opportunity import OpportunityResponse

        data = {
            "id": "opp-1",
            "user_id": "u-1",
            "status": "saved",
            "title": "Match Job",
            "url": "https://example.com",
            "match_score": 85.5,
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = OpportunityResponse(**data)
        assert resp.match_score == 85.5

    def test_opportunity_response_missing_url_raises(self):
        from database.schemas.opportunity import OpportunityResponse

        with pytest.raises(ValueError):
            OpportunityResponse(id="opp-1", user_id="u-1", status="saved", title="T")


# ─── Project ────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestProjectSchemas:
    """ProjectCreate, ProjectUpdate, ProjectResponse"""

    def test_project_create_requires_title(self):
        from database.schemas.project import ProjectCreate

        p = ProjectCreate(title="Portfolio Site")
        assert p.title == "Portfolio Site"
        assert p.phase == "planning"

    def test_project_create_with_optionals(self):
        from database.schemas.project import ProjectCreate

        p = ProjectCreate(
            title="CLI Tool",
            description="A Rust CLI",
            phase="development",
            github_url="https://github.com/user/cli",
            live_url="https://cli.example.com",
            next_action="Write tests",
        )
        assert p.github_url == "https://github.com/user/cli"
        assert p.next_action == "Write tests"
        assert p.phase == "development"

    def test_project_update_partial(self):
        from database.schemas.project import ProjectUpdate

        u = ProjectUpdate(phase="deployed", github_url="https://github.com/u/app")
        assert u.phase == "deployed"
        assert u.github_url == "https://github.com/u/app"
        assert u.title is None

    def test_project_response_from_dict(self):
        from database.schemas.project import ProjectResponse

        data = {
            "id": "p-1",
            "user_id": "u-1",
            "title": "My App",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = ProjectResponse(**data)
        assert resp.id == "p-1"
        assert resp.phase == "planning"

    def test_project_response_all_fields(self):
        from database.schemas.project import ProjectResponse

        data = {
            "id": "p-1",
            "user_id": "u-1",
            "title": "Full App",
            "description": "Desc",
            "phase": "launched",
            "github_url": "https://github.com/u/app",
            "live_url": "https://app.example.com",
            "next_action": "Marketing",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = ProjectResponse(**data)
        assert resp.phase == "launched"
        assert resp.github_url == "https://github.com/u/app"

    def test_project_response_missing_title_raises(self):
        from database.schemas.project import ProjectResponse

        with pytest.raises(ValueError):
            ProjectResponse(id="p-1", user_id="u-1")


# ─── Resource ───────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestResourceSchemas:
    """ResourceCreate, ResourceUpdate, ResourceResponse"""

    def test_resource_create_requires_title_and_url(self):
        from database.schemas.resource import ResourceCreate

        r = ResourceCreate(title="React Docs", url="https://react.dev")
        assert r.title == "React Docs"
        assert r.url == "https://react.dev"
        assert r.resource_type == "article"

    def test_resource_create_missing_url_raises(self):
        from database.schemas.resource import ResourceCreate

        with pytest.raises(ValueError):
            ResourceCreate(title="Resource")

    def test_resource_create_with_optionals(self):
        from database.schemas.resource import ResourceCreate

        r = ResourceCreate(
            title="FastAPI Guide",
            url="https://fastapi.tiangolo.com",
            resource_type="documentation",
            tags=["python", "api"],
            notes="Read later",
        )
        assert r.resource_type == "documentation"
        assert r.tags == ["python", "api"]

    def test_resource_update_partial(self):
        from database.schemas.resource import ResourceUpdate

        u = ResourceUpdate(is_archived=True, resource_type="video")
        assert u.is_archived is True
        assert u.resource_type == "video"

    def test_resource_response_from_dict(self):
        from database.schemas.resource import ResourceResponse

        data = {
            "id": "res-1",
            "user_id": "u-1",
            "title": "Tutorial",
            "url": "https://example.com",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = ResourceResponse(**data)
        assert resp.title == "Tutorial"
        assert resp.is_archived is False

    def test_resource_response_missing_title_raises(self):
        from database.schemas.resource import ResourceResponse

        with pytest.raises(ValueError):
            ResourceResponse(id="res-1", user_id="u-1", url="https://example.com")


# ─── Sleep ──────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestSleepSchemas:
    """SleepCreate, SleepUpdate, SleepResponse"""

    def test_sleep_create_requires_bedtime_wake_time_quality(self):
        from database.schemas.sleep import SleepCreate

        s = SleepCreate(bedtime="23:00", wake_time="07:00", quality_rating=3)
        assert s.bedtime == "23:00"
        assert s.wake_time == "07:00"
        assert s.quality_rating == 3

    def test_sleep_create_with_values(self):
        from database.schemas.sleep import SleepCreate

        s = SleepCreate(
            bedtime="23:00",
            wake_time="07:00",
            quality_rating=4,
        )
        assert s.bedtime == "23:00"
        assert s.quality_rating == 4

    def test_sleep_create_quality_zero(self):
        from database.schemas.sleep import SleepCreate

        s = SleepCreate(bedtime="00:00", wake_time="06:00", quality_rating=0)
        assert s.quality_rating == 0

    def test_sleep_create_missing_bedtime_raises(self):
        from database.schemas.sleep import SleepCreate

        with pytest.raises(ValueError):
            SleepCreate()

    def test_sleep_response_from_dict(self):
        from database.schemas.sleep import SleepResponse

        data = {
            "id": "sl-1",
            "user_id": "u-1",
            "bedtime": "23:00",
            "wake_time": "07:00",
            "quality_rating": 3,
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = SleepResponse(**data)
        assert resp.id == "sl-1"
        assert resp.quality_rating == 3

    def test_sleep_response_all_fields(self):
        from database.schemas.sleep import SleepResponse

        data = {
            "id": "sl-1",
            "user_id": "u-1",
            "bedtime": "23:00",
            "wake_time": "07:00",
            "quality_rating": 4,
            "duration_hours": 8.0,
            "sleep_score": 90,
            "sleep_debt": 1.5,
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = SleepResponse(**data)
        assert resp.duration_hours == 8.0
        assert resp.sleep_score == 90
        assert resp.quality_rating == 4
        assert resp.sleep_debt == 1.5

    def test_sleep_response_missing_bedtime_raises(self):
        from database.schemas.sleep import SleepResponse

        with pytest.raises(ValueError):
            SleepResponse(id="sl-1", user_id="u-1", wake_time="07:00", quality_rating=3)


# ─── Task (verify existing coverage) ────────────────────────────────────────


@pytest.mark.schema
class TestTaskSchemas:
    """TaskCreate, TaskUpdate, TaskResponse — verify coverage"""

    def test_task_create_requires_title(self):
        from database.schemas.task import TaskCreate

        t = TaskCreate(title="Write tests")
        assert t.title == "Write tests"
        assert t.priority == "medium"
        assert t.category == "personal"
        assert t.is_recurring is False

    def test_task_create_with_all_optionals(self):
        from database.schemas.task import TaskCreate

        t = TaskCreate(
            title="Ship feature",
            description="Deploy to prod",
            priority="urgent",
            category="project",
            estimated_minutes=120,
            due_date=datetime(2026, 7, 1),
            goal_id="goal-1",
            project_id="proj-1",
            dependency_id="task-0",
            is_recurring=True,
            recurring_frequency="weekly",
        )
        assert t.priority == "urgent"
        assert t.estimated_minutes == 120
        assert t.is_recurring is True
        assert t.recurring_frequency == "weekly"

    def test_task_create_invalid_priority_raises(self):
        from database.schemas.task import TaskCreate

        with pytest.raises(ValueError):
            TaskCreate(title="Test", priority="super_urgent")

    def test_task_create_invalid_category_raises(self):
        from database.schemas.task import TaskCreate

        with pytest.raises(ValueError):
            TaskCreate(title="Test", category="unknown")

    def test_task_update_all_optional(self):
        from database.schemas.task import TaskUpdate

        u = TaskUpdate(status="completed")
        assert u.status == "completed"
        assert u.title is None

    def test_task_update_empty(self):
        from database.schemas.task import TaskUpdate

        u = TaskUpdate()
        assert u.title is None
        assert u.status is None

    def test_task_response_from_dict(self):
        from database.schemas.task import TaskResponse

        now = datetime.now()
        data = {
            "id": "t-1",
            "user_id": "u-1",
            "status": "in_progress",
            "title": "Code review",
            "priority": "medium",
            "category": "project",
            "completed_at": None,
            "missed_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        resp = TaskResponse(**data)
        assert resp.status == "in_progress"
        assert resp.missed_count == 0
        assert resp.completed_at is None

    def test_task_response_enum_values(self):
        from database.schemas.task import TaskResponse, Priority, Category, TaskStatus

        now = datetime.now()
        data = {
            "id": "t-1",
            "user_id": "u-1",
            "status": "completed",
            "title": "Task",
            "priority": "low",
            "category": "study",
            "completed_at": now,
            "missed_count": 2,
            "created_at": now,
            "updated_at": now,
        }
        resp = TaskResponse(**data)
        assert resp.status == TaskStatus.completed
        assert resp.priority == Priority.low
        assert resp.category == Category.study

    def test_task_response_invalid_status_raises(self):
        from database.schemas.task import TaskResponse

        now = datetime.now()
        with pytest.raises(ValueError):
            TaskResponse(
                id="t-1",
                user_id="u-1",
                status="invalid_status",
                title="T",
                priority="medium",
                category="personal",
                completed_at=None,
                missed_count=0,
                created_at=now,
                updated_at=now,
            )

    def test_task_create_enum_by_value(self):
        from database.schemas.task import TaskCreate

        t = TaskCreate(title="Test", priority="high", category="study")
        assert t.priority.value == "high"
        assert t.category.value == "study"


# ─── TimeEntry ──────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestTimeEntrySchemas:
    """TimeEntryCreate, TimeEntryUpdate, TimeEntryResponse"""

    def test_time_entry_create_requires_start_time(self):
        from database.schemas.time_entry import TimeEntryCreate

        now = datetime.now()
        te = TimeEntryCreate(start_time=now)
        assert te.start_time == now
        assert te.category == "work"

    def test_time_entry_create_with_optionals(self):
        from database.schemas.time_entry import TimeEntryCreate

        now = datetime.now()
        te = TimeEntryCreate(
            task_id="task-1",
            project_id="proj-1",
            start_time=now,
            end_time=now,
            duration_minutes=60,
            description="Worked on feature",
            category="development",
        )
        assert te.task_id == "task-1"
        assert te.duration_minutes == 60
        assert te.category == "development"

    def test_time_entry_create_missing_start_time_raises(self):
        from database.schemas.time_entry import TimeEntryCreate

        with pytest.raises(ValueError):
            TimeEntryCreate()

    def test_time_entry_update_all_optional(self):
        from database.schemas.time_entry import TimeEntryUpdate

        u = TimeEntryUpdate(duration_minutes=90, category="meeting")
        assert u.duration_minutes == 90
        assert u.start_time is None

    def test_time_entry_update_empty(self):
        from database.schemas.time_entry import TimeEntryUpdate

        u = TimeEntryUpdate()
        assert u.task_id is None
        assert u.category is None

    def test_time_entry_response_from_dict(self):
        from database.schemas.time_entry import TimeEntryResponse

        data = {
            "id": "te-1",
            "user_id": "u-1",
            "task_id": None,
            "project_id": None,
            "start_time": "2026-06-17T10:00:00Z",
            "end_time": None,
            "duration_minutes": None,
            "description": None,
            "category": "work",
            "created_at": "2026-06-01T12:00:00Z",
        }
        resp = TimeEntryResponse(**data)
        assert resp.id == "te-1"
        assert resp.category == "work"
        assert resp.task_id is None

    def test_time_entry_response_all_fields(self):
        from database.schemas.time_entry import TimeEntryResponse

        data = {
            "id": "te-1",
            "user_id": "u-1",
            "task_id": "task-1",
            "project_id": "proj-1",
            "start_time": "2026-06-17T10:00:00Z",
            "end_time": "2026-06-17T11:00:00Z",
            "duration_minutes": 60,
            "description": "Coding session",
            "category": "development",
            "created_at": "2026-06-17T10:00:00Z",
        }
        resp = TimeEntryResponse(**data)
        assert resp.duration_minutes == 60
        assert resp.description == "Coding session"

    def test_time_entry_response_missing_required_raises(self):
        from database.schemas.time_entry import TimeEntryResponse

        with pytest.raises(ValueError):
            TimeEntryResponse(id="te-1", user_id="u-1")


# ─── User ───────────────────────────────────────────────────────────────────


@pytest.mark.schema
class TestUserSchemas:
    """UserCreate, UserUpdate, UserResponse"""

    def test_user_create_requires_email(self):
        from database.schemas.user import UserCreate

        u = UserCreate(email="test@example.com")
        assert u.email == "test@example.com"
        assert u.skills == []
        assert u.name is None

    def test_user_create_missing_email_raises(self):
        from database.schemas.user import UserCreate

        with pytest.raises(ValueError):
            UserCreate()

    def test_user_create_with_optionals(self):
        from database.schemas.user import UserCreate

        u = UserCreate(
            email="dev@example.com",
            name="Dev User",
            avatar_url="https://avatar.com/me.png",
            college="MIT",
            year=3,
            skills=["Python", "React"],
            bio="Full-stack dev",
        )
        assert u.name == "Dev User"
        assert u.college == "MIT"
        assert u.year == 3
        assert u.skills == ["Python", "React"]

    def test_user_update_with_extra_fields(self):
        from database.schemas.user import UserUpdate

        u = UserUpdate(
            name="New Name",
            daily_routine={"wake": "7AM", "sleep": "11PM"},
            opportunity_preferences={"internships": True},
        )
        assert u.name == "New Name"
        assert u.daily_routine == {"wake": "7AM", "sleep": "11PM"}
        assert u.opportunity_preferences == {"internships": True}

    def test_user_update_partial(self):
        from database.schemas.user import UserUpdate

        u = UserUpdate(bio="Updated bio")
        assert u.bio == "Updated bio"
        assert u.name is None

    def test_user_update_empty(self):
        from database.schemas.user import UserUpdate

        u = UserUpdate()
        assert u.name is None
        assert u.skills is None

    def test_user_response_from_dict(self):
        from database.schemas.user import UserResponse

        data = {
            "id": "u-1",
            "email": "user@example.com",
            "created_at": "2026-06-01T12:00:00Z",
            "updated_at": "2026-06-01T12:00:00Z",
        }
        resp = UserResponse(**data)
        assert resp.id == "u-1"
        assert resp.email == "user@example.com"
        assert resp.skills == []

    def test_user_response_all_fields(self):
        from database.schemas.user import UserResponse

        data = {
            "id": "u-1",
            "email": "full@example.com",
            "name": "Full User",
            "avatar_url": "https://img.com/a.png",
            "college": "Stanford",
            "year": 4,
            "skills": ["AI", "Systems"],
            "bio": "CS major",
            "created_at": "2026-06-01T12:00:00Z",
            "updated_at": "2026-06-01T12:00:00Z",
        }
        resp = UserResponse(**data)
        assert resp.year == 4
        assert resp.college == "Stanford"
        assert resp.skills == ["AI", "Systems"]

    def test_user_response_missing_email_raises(self):
        from database.schemas.user import UserResponse

        with pytest.raises(ValueError):
            UserResponse(id="u-1")
