"""Pure, dependency-free text entity extraction shared by the NLP route and ARIA.

These three functions used to live only in ``apps/api/app/api/nlp.py``. Two very
different callers need them:

* ``app/api/nlp.py`` -- the ``/api/v1/nlp/parse`` route.
* ``ai/intent.py``    -- ARIA's intent classifier.

``packages/*`` cannot import ``app.api.*``: ``apps/api`` is only on ``sys.path``
for the API process, and importing a route module from a library module would
drag FastAPI routers into the scheduler and the agent registry. Duplicating the
bodies instead would guarantee the two copies drift.

So the logic lives here, in the lowest layer both can reach, and ``nlp.py``
re-exports the names unchanged. Every existing ``from app.api.nlp import
extract_date`` call site -- including the tests -- keeps working, against one
implementation.
"""

import re
from datetime import datetime, timedelta
from typing import Optional

DAY_NAMES = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6,
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}

# ``d/d`` or ``d/d/yy`` or ``d/d/yyyy``.
_DATE_SLASH_RE = re.compile(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?")
# "in 3 days", "in 2 weeks".
_RELATIVE_RE = re.compile(r"in\s+(\d+)\s+(day|days|week|weeks)")
_HIGH_PRIORITY_RE = re.compile(r"\b(urgent|critical|asap|high priority|important)\b")
_LOW_PRIORITY_RE = re.compile(r"\b(low priority|whenever|someday|optional)\b")
# Longest-first so "hours" is not shadowed by "hour" inside the same alternation.
_DURATION_RE = re.compile(r"(\d+)\s*(mins|min|minute|minutes|hour|hours|hr|hrs)\b")


def extract_date(text: str) -> Optional[str]:
    """Resolve a natural-language date phrase to ``YYYY-MM-DD``, or None.

    Unchanged behaviour from the original in-route implementation: relative day
    names resolve to the *next* occurrence of that weekday (today counts as
    itself), and an unparseable phrase returns None rather than guessing.
    """
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    lower = text.lower()

    if "today" in lower:
        return today
    if "tomorrow" in lower:
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")

    for name, idx in DAY_NAMES.items():
        if name in lower:
            target = now + timedelta(days=(idx - now.weekday() + 7) % 7)
            return target.strftime("%Y-%m-%d")

    match = _DATE_SLASH_RE.search(text)
    if match:
        m, d, y = match.groups()
        year = y if y else str(now.year)
        if len(year) == 2:
            year = f"20{year}"
        return f"{year}-{m.zfill(2)}-{d.zfill(2)}"

    rel = _RELATIVE_RE.search(lower)
    if rel:
        num = int(rel.group(1))
        unit = rel.group(2).lower()
        target = now + timedelta(days=num * 7) if unit.startswith("week") else now + timedelta(days=num)
        return target.strftime("%Y-%m-%d")

    return None


def extract_priority(text: str) -> Optional[str]:
    """Map urgency wording to ``high``/``low``, or None when unstated."""
    lower = text.lower()
    if _HIGH_PRIORITY_RE.search(lower):
        return "high"
    if _LOW_PRIORITY_RE.search(lower):
        return "low"
    return None


def extract_minutes(text: str) -> Optional[int]:
    """Convert ``"90 mins"`` / ``"2 hours"`` into a minute count, or None."""
    match = _DURATION_RE.search(text.lower())
    if not match:
        return None
    num = int(match.group(1))
    unit = match.group(2).lower()
    return num * 60 if unit.startswith(("hour", "hr")) else num
