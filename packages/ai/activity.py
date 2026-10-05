"""One row per agent step, in `agent_activity_log`.

The table exists (`scripts/migrations/008_agent_activity_log.sql`), the read
endpoint exists (`GET /api/v1/monitoring/activity`), and
`POST /api/v1/monitoring/activity` exists to write it -- but nothing in the
codebase ever called it. `get_metrics` reads the table to compute an error rate,
so the error rate was structurally always 0%.

The column set here is the migration's, not AGENTS.md's. AGENTS.md §7.1 claims
`agent_activity` has `agent_id`; the migration has no such column. Writing
`agent_id` would fail the insert, and Supabase reports that on `response.error`
rather than raising, so the failure would be silent. The columns below are the
ones that exist:

    id, user_id, agent_name, status, started_at, completed_at,
    duration_ms, error_message, input_summary, output_summary, created_at

`status` is CHECK-constrained to running/completed/failed, so nothing else may be
written.

Writes go straight to Supabase rather than through the HTTP endpoint. The
orchestrator runs in-process inside the API; an HTTP round trip to its own
server to log an activity row would add latency to every agent step and would
deadlock under a single-worker deployment.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger

# The CHECK constraint in the migration. Writing anything else fails the insert.
VALID_STATUSES = frozenset({"running", "completed", "failed"})

# Summaries are stored as text, and an unbounded agent output would bloat every
# row of the feed. Truncated at the boundary rather than in the UI.
MAX_SUMMARY_CHARS = 500


def _summarise(value: Any, limit: int = MAX_SUMMARY_CHARS) -> Optional[str]:
    """Render any agent output as a bounded single-line string.

    Agent outputs are heterogeneous: dicts, lists, Pydantic models, strings.
    Nothing here trusts them to be any particular type.
    """
    if value is None:
        return None
    if isinstance(value, str):
        text = value
    else:
        try:
            import json

            text = json.dumps(value, default=str)
        except Exception:  # noqa: BLE001 -- summarisation must never raise
            text = str(value)
    text = " ".join(text.split())
    if not text:
        return None
    if len(text) > limit:
        text = text[:limit] + "..."
    return text


async def record_activity(
    user_id: str,
    agent_name: str,
    status: str,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    duration_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    input_summary: Any = None,
    output_summary: Any = None,
) -> Optional[str]:
    """Append one activity row. Returns the row id, or None if it could not be written.

    Never raises. Logging is observability, not business logic: an agent that
    succeeded must not be reported as failed because its activity row did not
    land, and a request must not 500 because the audit table is unavailable.
    """
    if status not in VALID_STATUSES:
        logger.warn(
            "Agent activity status violates the table CHECK constraint; coercing to failed",
            agent=agent_name,
            requested_status=status,
        )
        status = "failed"

    now = datetime.now(timezone.utc)
    record: Dict[str, Any] = {
        "id": str(uuid4()),
        "user_id": user_id,
        "agent_name": agent_name,
        "status": status,
        "started_at": (started_at or now).isoformat(),
        "completed_at": completed_at.isoformat() if completed_at else None,
        "duration_ms": duration_ms,
        "error_message": _summarise(error_message, limit=300),
        "input_summary": _summarise(input_summary),
        "output_summary": _summarise(output_summary),
        "created_at": now.isoformat(),
    }

    try:
        supabase = get_supabase_client()
        result = supabase.from_("agent_activity_log").insert(record).execute()
    except Exception as exc:  # noqa: BLE001 -- never propagate into the agent run
        logger.warn("Agent activity insert raised", agent=agent_name, error=str(exc))
        return None

    # Supabase reports RLS rejections and constraint violations on
    # `response.error`, not by raising. Without this check a permanently
    # misconfigured table looks exactly like a working one.
    error = getattr(result, "error", None)
    if error:
        message = getattr(error, "message", None) or str(error)
        logger.error("Agent activity insert rejected by database", agent=agent_name, error=message)
        return None

    return record["id"]
