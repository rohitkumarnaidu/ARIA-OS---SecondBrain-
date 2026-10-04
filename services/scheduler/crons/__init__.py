"""Scheduler cron job package.

Re-export facade for every cron job entrypoint. Importing any submodule of this
package executes this file, so these imports are deliberately eager: they are
the package's public API surface (``from crons import run_daily_briefing``) and
they also guarantee every cron module is loaded before APScheduler starts.

``__all__`` declares the intent explicitly so linters treat these names as used
rather than as accidental unused imports.
"""

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
from crons.health_check import run_health_check
from crons.deadline_alert import run_deadline_alert
from crons.memory_consolidation import run_memory_consolidation

__all__ = [
    "run_daily_briefing",
    "run_radar",
    "run_weekly_review",
    "run_habit_checker",
    "run_missed_task_checker",
    "run_sleep_reminder",
    "run_course_nudges",
    "run_skill_intelligence_refresh",
    "run_skill_evidence_expiry",
    "run_skill_analytics_snapshot",
    "run_skill_mv_refresh",
    "run_skill_retention_cleanup",
    "run_health_check",
    "run_deadline_alert",
    "run_memory_consolidation",
]
