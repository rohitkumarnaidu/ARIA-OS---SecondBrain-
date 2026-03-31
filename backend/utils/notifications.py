import os
from typing import Optional


def send_push_notification(
    user_id: str, title: str, body: str, data: Optional[dict] = None
) -> bool:
    print(f"[PUSH] To user {user_id}: {title} - {body}")
    return True


def send_email_notification(email: str, subject: str, body: str) -> bool:
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        print(f"[EMAIL] To {email}: {subject}")
        return True

    print(f"[EMAIL] Sending to {email}: {subject}")
    return True


def send_sms_notification(phone: str, message: str) -> bool:
    print(f"[SMS] To {phone}: {message}")
    return True


def notify_task_overdue(task_title: str, user_email: str):
    send_email_notification(
        user_email,
        f"Overdue Task: {task_title}",
        f"Your task '{task_title}' is overdue. Please complete or reschedule it.",
    )


def notify_critical_alert(alert_message: str, user_phone: str):
    send_sms_notification(user_phone, f"ALERT: {alert_message}")


def notify_habit_missed(habit_name: str, user_email: str):
    send_email_notification(
        user_email,
        f"Habit Missed: {habit_name}",
        f"You missed your habit '{habit_name}' today. Don't worry, tomorrow is a new day!",
    )


def notify_bedtime_reminder(user_email: str, bedtime: str):
    send_email_notification(
        user_email,
        "Bedtime Reminder",
        f"It's {bedtime}. Time to start winding down for a good night's sleep.",
    )
