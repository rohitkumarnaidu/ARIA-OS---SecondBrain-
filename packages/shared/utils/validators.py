from typing import Optional
from datetime import datetime

from shared.utils.security import sanitize_object


def validate_task_data(title: str, priority: str = "medium", category: str = "personal") -> dict:
    errors = []

    if not title or len(title.strip()) < 1:
        errors.append("Title is required")
    elif len(title) > 200:
        errors.append("Title must be less than 200 characters")

    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")

    valid_categories = ["study", "project", "habit", "personal", "income"]
    if category not in valid_categories:
        errors.append(f"Category must be one of: {', '.join(valid_categories)}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_due_date(due_date: Optional[str]) -> bool:
    if not due_date:
        return True
    try:
        datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_recurring_frequency(frequency: Optional[str]) -> bool:
    if not frequency:
        return True
    valid_frequencies = ["daily", "weekly", "monthly"]
    return frequency in valid_frequencies


VALID_TASK_STATUSES = ["pending", "in_progress", "completed", "cancelled"]
VALID_TASK_PRIORITIES = ["low", "medium", "high", "urgent"]
VALID_PROJECT_PHASES = ["ideation", "planning", "execution", "review", "completed"]


def validate_task_input(data: dict) -> list[str]:
    errors = []
    title = data.get("title", "")
    if not title or not title.strip():
        errors.append("title is required")
    elif len(title) > 200:
        errors.append("title must be at most 200 characters")
    status = data.get("status")
    if status and status not in VALID_TASK_STATUSES:
        errors.append(f"status must be one of: {', '.join(VALID_TASK_STATUSES)}")
    priority = data.get("priority")
    if priority and priority not in VALID_TASK_PRIORITIES:
        errors.append(f"priority must be one of: {', '.join(VALID_TASK_PRIORITIES)}")
    return errors


def validate_project_input(data: dict) -> list[str]:
    errors = []
    title = data.get("title", "")
    if not title or not title.strip():
        errors.append("title is required")
    phase = data.get("phase")
    if phase and phase not in VALID_PROJECT_PHASES:
        errors.append(f"phase must be one of: {', '.join(VALID_PROJECT_PHASES)}")
    return errors


def validate_date_range(start: str, end: str) -> bool:
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return start_dt <= end_dt
    except (ValueError, TypeError):
        return False


VALIDATION_SCHEMAS = {
    "task": validate_task_input,
    "project": validate_project_input,
}


def sanitize_and_validate(data: dict, schema_type: str) -> tuple[dict, list[str]]:
    sanitized = sanitize_object(data)
    validator = VALIDATION_SCHEMAS.get(schema_type)
    if not validator:
        return sanitized, [f"unknown schema type: {schema_type}"]
    errors = validator(sanitized)
    return sanitized, errors
