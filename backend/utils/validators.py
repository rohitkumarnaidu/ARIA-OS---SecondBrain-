from typing import Optional, List
from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


def validate_task_data(
    title: str, priority: str = "medium", category: str = "personal"
) -> dict:
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
        due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_recurring_frequency(frequency: Optional[str]) -> bool:
    if not frequency:
        return True
    valid_frequencies = ["daily", "weekly", "monthly"]
    return frequency in valid_frequencies
