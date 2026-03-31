from datetime import datetime, timedelta
from typing import Optional


def get_current_iso() -> str:
    return datetime.now().isoformat()


def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def days_until(date_str: str) -> int:
    target = parse_date(date_str)
    if not target:
        return 0
    return (target - datetime.now()).date()).days


def format_relative_time(dt: datetime) -> str:
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "just now"


def get_week_range() -> tuple:
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_range() -> tuple:
    today = datetime.now().date()
    start = today.replace(day=1)
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return start, end


def is_overdue(due_date: Optional[str]) -> bool:
    if not due_date:
        return False
    due = parse_date(due_date)
    return due and due < datetime.now()


def get_next_occurrence(day_of_week: int) -> datetime:
    today = datetime.now()
    days_ahead = day_of_week - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)