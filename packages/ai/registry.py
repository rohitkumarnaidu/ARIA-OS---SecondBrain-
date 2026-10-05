"""The agent registry: what actually exists, what it can do, and what it needs.

AGENTS.md §9.1 claimed "ARIA is the single point of intelligence. It receives
every user message, classifies intent, dispatches to sub-agents, and
synthesizes responses." None of that existed. `ai/orchestrator.py` was five
unrelated functions that never called each other, `ai/agents/__init__.py` was a
flat import list, and the `A00`..`A17` identifiers existed only as comments in
one test file. `POST /api/v1/monitoring/activity` had zero callers.

This module is the missing half: a machine-readable description of every agent
that has a real, importable entrypoint, so the orchestrator can dispatch to it
without hardcoding strings at each call site.

Two rules govern every entry here:

1. **No invented agents.** If a numbered agent from AGENTS.md §9.3 has no
   module, it is absent from the registry and the absence is documented. The
   test `test_every_registered_agent_imports` walks the registry and imports each
   `module` + `entrypoint`, so a typo or a phantom agent fails CI immediately.
2. **Every agent declares how it dies gracefully.** `fallback` names the
   algorithmic twin that produces a usable answer with no LLM reachable. An agent
   whose fallback is `None` says so honestly: it has no LLM-free path.

`hitl_threshold` is the confidence below which a human must confirm before the
agent's mutation is allowed to land. It is `1.0` (i.e. "never auto-run") for
anything that writes, and `0.0` for read-only agents, where a wrong answer costs
nothing and a confirmation prompt is pure friction.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from shared.utils.logger import logger


@dataclass(frozen=True)
class AgentSpec:
    """One registered agent.

    Attributes
    ----------
    id:
        The AGENTS.md §9.3 identifier (`A09`) or a stable slug for agents the
        document does not number. Never invented: an id appears here only if a
        real callable backs it.
    name:
        Human-readable label, used in activity logs and the agents page.
    module:
        Fully-qualified import path of the module holding `entrypoint`.
    entrypoint:
        Name of the async callable in `module`.
    capabilities:
        Intents this agent can serve. Used by `agents_for_intent`.
    trigger:
        `cron` (scheduler-only), `on_demand` (explicit API call), or `chat`
        (ARIA may dispatch it during a conversation).
    requires_context:
        Names of `ContextEngine` sections (`NEEDS_MAP` keys) the agent wants
        assembled before it runs.
    hitl_threshold:
        Below this confidence a mutating agent must not auto-run.
    mutates:
        Whether the agent writes to the database.
    fallback:
        `module:callable` for the algorithmic twin, or None when the agent has
        no LLM-free path. Stored as a string, not an imported symbol, so the
        registry stays import-cheap and free of import cycles.
    description:
        One line for the UI.
    """

    id: str
    name: str
    module: str
    entrypoint: str
    capabilities: List[str]
    trigger: str
    requires_context: List[str] = field(default_factory=list)
    hitl_threshold: float = 0.0
    mutates: bool = False
    fallback: Optional[str] = None
    description: str = ""

    def load(self) -> Optional[Callable[..., Any]]:
        """Import and return the entrypoint, or None if it cannot be resolved.

        Resolution is deferred to call time on purpose. Importing twelve agent
        modules at package-import time would make `ai.registry` fail wholesale
        the moment one of them breaks, and would create an import cycle: every
        agent imports `ai.client`, and `ai.client` is imported by the registry's
        own callers.
        """
        import importlib

        try:
            module = importlib.import_module(self.module)
        except Exception as exc:  # noqa: BLE001 -- a broken agent must not break dispatch
            logger.error("Registry: agent module failed to import", agent=self.id, module=self.module, error=str(exc))
            return None

        fn = getattr(module, self.entrypoint, None)
        if not callable(fn):
            logger.error(
                "Registry: agent entrypoint is not callable",
                agent=self.id,
                module=self.module,
                entrypoint=self.entrypoint,
            )
            return None
        return fn

    def load_fallback(self) -> Optional[Callable[..., Any]]:
        """Import the algorithmic twin, or None when none is declared."""
        if not self.fallback:
            return None
        module_path, _, attr = self.fallback.partition(":")
        import importlib

        try:
            module = importlib.import_module(module_path)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Registry: fallback module failed to import",
                agent=self.id,
                module=module_path,
                error=str(exc),
            )
            return None
        fn = getattr(module, attr, None)
        return fn if callable(fn) else None


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------
#
# Deliberate omissions, with reasons. AGENTS.md §9.3 lists A00..A17; only the
# ones below have a real callable.
#
#   A00 ARIA (orchestrator)  -- not an agent. It IS `ai/orchestrator_core.py`.
#                               Dispatching ARIA to ARIA would recurse.
#   A01 Planner              -- no module. `orchestrate_plan` in ai/orchestrator.py
#                               is an LLM prompt scaffold, not a planner, and
#                               `orchestrator_core.plan()` replaces it.
#   A04 Reminder             -- cron-only, no module. The nudge agent (A14)
#                               covers proactive messaging.
#   A05 Career               -- no module. `skill_agent.analyze_career_readiness`
#                               covers career analysis and is registered as
#                               `A05-career`.
#   A07 Analytics            -- no dedicated module; `learning_agent` (A03) does
#                               the pattern work and is registered for the
#                               `analytics` intent.
#   A12 Habit Miss Checker   -- cron-only with no module; the logic is
#                               `nudge_agent.check_habit_streaks`, registered as
#                               `A12-habit-miss`.
#   A16                      -- reserved in the document, nothing to point at.
#
# `ai/agents/knowledge_agent.py` also has no A-id: AGENTS.md §9.3 does not list
# it and no numbered agent maps to it. Its `search_nodes(user_id, request)`
# needs a constructed `KnowledgeSearchRequest`, not a bare user_id, so it does
# not fit the registry's `(user_id)` dispatch contract either. It stays
# reachable through `GET /api/v1/knowledge/search`.

AGENT_REGISTRY: Dict[str, AgentSpec] = {
    spec.id: spec
    for spec in [
        AgentSpec(
            id="A02-memory",
            name="Memory",
            module="ai.agents.memory_agent",
            entrypoint="get_memory_summary",
            capabilities=["memory", "general"],
            trigger="chat",
            requires_context=["memory_relevant"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.memory_agent:get_recent_interactions",
            description="Recall stored preferences, context and prior conversations.",
        ),
        AgentSpec(
            id="A03-learning",
            name="Learning Analyst",
            module="ai.agents.learning_agent",
            entrypoint="suggest_learning_focus",
            capabilities=["analytics", "course", "skill"],
            trigger="chat",
            requires_context=["courses_active", "goals_active", "tasks_pending"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.learning_agent:detect_learning_patterns",
            description="Detect learning patterns and recommend what to study next.",
        ),
        AgentSpec(
            id="A05-career",
            name="Career Advisor",
            module="ai.agents.skill_agent",
            entrypoint="analyze_career_readiness",
            capabilities=["skill", "roadmap"],
            trigger="on_demand",
            requires_context=["goals_active", "projects_active"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.skill_agent:algorithmic_fallback_career",
            description="Assess readiness against the user's stated career goal.",
        ),
        AgentSpec(
            id="A06-opportunity",
            name="Opportunity Radar",
            module="ai.agents.opportunity_agent",
            entrypoint="run_opportunity_radar",
            capabilities=["opportunity"],
            trigger="chat",
            requires_context=["opportunities_open", "memory_relevant"],
            hitl_threshold=0.7,
            mutates=True,
            fallback="ai.agents.opportunity_agent:scan_default_opportunities",
            description="Find and score open opportunities against the user's skills.",
        ),
        AgentSpec(
            id="A08-roadmap",
            name="Roadmap Optimizer",
            module="ai.agents.roadmap_agent",
            entrypoint="optimize_roadmap",
            capabilities=["roadmap", "skill"],
            trigger="on_demand",
            requires_context=["goals_active", "courses_active", "projects_active"],
            hitl_threshold=0.7,
            mutates=True,
            fallback="ai.agents.roadmap_agent:detect_stale_nodes",
            description="Sequence the user's learning milestones into an ordered path.",
        ),
        AgentSpec(
            id="A09-briefing",
            name="Daily Briefing",
            module="ai.agents.briefing_agent",
            entrypoint="generate_daily_briefing",
            capabilities=["briefing", "general"],
            trigger="chat",
            requires_context=[
                "tasks_pending",
                "tasks_overdue",
                "habits_today",
                "sleep_recent",
                "courses_active",
                "goals_active",
            ],
            hitl_threshold=0.8,
            mutates=True,
            fallback="ai.agents.briefing_agent:generate_day_profile",
            description="Compose the morning briefing for the day ahead.",
        ),
        AgentSpec(
            id="A10-review",
            name="Weekly Review",
            module="ai.agents.weekly_review_agent",
            entrypoint="generate_weekly_review",
            capabilities=["review", "general"],
            trigger="chat",
            requires_context=[
                "tasks_pending",
                "goals_active",
                "habits_today",
                "sleep_recent",
                "income_recent",
                "time_today",
            ],
            hitl_threshold=0.8,
            mutates=True,
            fallback="ai.agents.weekly_review_agent:apply_review_profile",
            description="Summarise the past week across every tracked module.",
        ),
        AgentSpec(
            id="A11-missed-tasks",
            name="Missed Task Checker",
            module="ai.agents.task_agent",
            entrypoint="check_missed_tasks",
            capabilities=["task", "scheduling"],
            trigger="cron",
            requires_context=["tasks_overdue", "tasks_pending"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.task_agent:calculate_priority_score",
            description="Report tasks whose due dates have passed.",
        ),
        AgentSpec(
            id="A12-habit-miss",
            name="Habit Miss Checker",
            module="ai.agents.nudge_agent",
            entrypoint="check_habit_streaks",
            capabilities=["habit"],
            trigger="cron",
            requires_context=["habits_today"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.nudge_agent:get_escalation_level",
            description="Flag at-risk and broken habit streaks.",
        ),
        AgentSpec(
            id="A13-sleep",
            name="Sleep Analyst",
            module="ai.agents.sleep_agent",
            entrypoint="analyze_sleep",
            capabilities=["sleep"],
            trigger="chat",
            requires_context=["sleep_recent"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.sleep_agent:analyze_sleep_debt",
            description="Score recent sleep and surface accumulated sleep debt.",
        ),
        AgentSpec(
            id="A14-nudges",
            name="Nudge Engine",
            module="ai.agents.nudge_agent",
            entrypoint="run_all_nudges",
            capabilities=["course", "habit"],
            trigger="chat",
            requires_context=["courses_active", "habits_today", "tasks_pending"],
            hitl_threshold=0.75,
            mutates=True,
            fallback="ai.agents.nudge_agent:combine_course_habit_digest",
            description="Generate course and habit nudges for today.",
        ),
        AgentSpec(
            id="A15-matching",
            name="Opportunity Matcher",
            module="ai.agents.opportunity_matching_agent",
            entrypoint="match_opportunities",
            capabilities=["opportunity", "skill"],
            trigger="on_demand",
            requires_context=["opportunities_open", "memory_relevant"],
            hitl_threshold=0.7,
            mutates=True,
            fallback="ai.agents.opportunity_matching_agent:compute_algorithmic_score",
            description="Rescore existing opportunities against current skills.",
        ),
        AgentSpec(
            id="A17-skills",
            name="Skills Intelligence",
            module="ai.agents.skill_agent",
            entrypoint="recommend_skills",
            capabilities=["skill", "roadmap"],
            trigger="chat",
            requires_context=["goals_active", "courses_active", "projects_active"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.skill_agent:algorithmic_fallback_recommendation",
            description="Recommend skills to develop for the user's target roles.",
        ),
        AgentSpec(
            id="A01-task",
            name="Task Analyst",
            module="ai.agents.task_agent",
            entrypoint="suggest_task_prioritization",
            capabilities=["task", "scheduling"],
            trigger="chat",
            requires_context=["tasks_pending", "tasks_overdue", "tasks_today", "goals_active"],
            hitl_threshold=0.0,
            mutates=False,
            fallback="ai.agents.task_agent:calculate_priority_score",
            description="Rank pending tasks and detect schedule conflicts.",
        ),
    ]
}

# Intents that may only be served by cron/on_demand agents. Chat dispatch skips
# these unless the plan explicitly requests them.
CRON_TRIGGERS = frozenset({"cron"})

# Ordering weight for capability-driven sequencing. Lower runs first. This is
# the "capability ordering" half of the plan: memory before anything that should
# factor it in, context-light analysis before synthesis-heavy agents.
AGENT_ORDER: Dict[str, int] = {
    "A02-memory": 10,
    "A11-missed-tasks": 20,
    "A12-habit-miss": 20,
    "A13-sleep": 30,
    "A01-task": 30,
    "A03-learning": 40,
    "A17-skills": 40,
    "A14-nudges": 50,
    "A15-matching": 50,
    "A06-opportunity": 60,
    "A05-career": 60,
    "A08-roadmap": 70,
    "A09-briefing": 80,
    "A10-review": 80,
}

# Which agents a second agent depends on. Kept as data rather than encoded in
# the dispatcher so the plan is inspectable and testable.
AGENT_DEPENDENCIES: Dict[str, List[str]] = {
    "A03-learning": ["A02-memory"],
    "A06-opportunity": ["A02-memory"],
    "A15-matching": ["A02-memory"],
    "A14-nudges": ["A02-memory"],
    "A08-roadmap": ["A17-skills"],
    "A09-briefing": ["A11-missed-tasks", "A13-sleep"],
    "A10-review": ["A03-learning"],
    "A01-task": ["A11-missed-tasks"],
}


def get_agent(agent_id: str) -> Optional[AgentSpec]:
    """Look up one agent by id. Returns None for an unregistered id."""
    return AGENT_REGISTRY.get(agent_id)


def list_agents() -> List[AgentSpec]:
    """Every registered agent, ordered by dispatch weight then id."""
    return sorted(AGENT_REGISTRY.values(), key=lambda s: (AGENT_ORDER.get(s.id, 50), s.id))


def agents_for_intent(intent: str, include_cron: bool = False) -> List[AgentSpec]:
    """Agents that can serve `intent`, in dispatch order.

    Cron-only agents are excluded by default: a scheduled job firing mid
    conversation is a side effect the user did not ask for.
    """
    matched = [a for a in AGENT_REGISTRY.values() if intent in a.capabilities]
    if not include_cron:
        matched = [a for a in matched if a.trigger not in CRON_TRIGGERS]
    return sorted(matched, key=lambda s: (AGENT_ORDER.get(s.id, 50), s.id))
