import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

RESEND_API_BASE = "https://api.resend.com/emails"
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01/Accounts"

NOTIFICATION_TYPES = {
    "email": "email",
    "push": "push",
    "sms": "sms",
}


def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> dict:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        logger.warning("RESEND_API_KEY not set, falling back to print")
        print(f"[EMAIL] To {to}: {subject}")
        return {"success": True, "message_id": None, "error": None}

    from_addr = os.getenv("RESEND_FROM_EMAIL", "ARIA OS <noreply@secondbrain-os.com>")
    payload = {
        "from": from_addr,
        "to": [to],
        "subject": subject,
        "text": body,
    }
    if html_body:
        payload["html"] = html_body

    try:
        resp = httpx.post(
            RESEND_API_BASE,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15.0,
        )
        if resp.is_success:
            data = resp.json()
            return {"success": True, "message_id": data.get("id"), "error": None}
        error_msg = f"Resend API error {resp.status_code}: {resp.text}"
        logger.error(error_msg)
        return {"success": False, "message_id": None, "error": error_msg}
    except httpx.TimeoutException:
        logger.error("Resend API request timed out")
        return {"success": False, "message_id": None, "error": "Request timed out"}
    except Exception as exc:
        logger.error("Resend API request failed: %s", exc)
        return {"success": False, "message_id": None, "error": str(exc)}


def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> dict:
    webhook_url = os.getenv("PUSH_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("PUSH_WEBHOOK_URL not set, falling back to print")
        print(f"[PUSH] To user {user_id}: {title} - {body}")
        return {"success": True, "message_id": None, "error": None}

    payload = {"user_id": user_id, "title": title, "body": body}
    if data:
        payload["data"] = data

    try:
        resp = httpx.post(webhook_url, json=payload, timeout=10.0)
        if resp.is_success:
            return {"success": True, "message_id": resp.json().get("id"), "error": None}
        error_msg = f"Push webhook error {resp.status_code}: {resp.text}"
        logger.error(error_msg)
        return {"success": False, "message_id": None, "error": error_msg}
    except httpx.TimeoutException:
        logger.error("Push webhook request timed out")
        return {"success": False, "message_id": None, "error": "Request timed out"}
    except Exception as exc:
        logger.error("Push webhook request failed: %s", exc)
        return {"success": False, "message_id": None, "error": str(exc)}


def send_sms(
    phone: str,
    message: str,
) -> dict:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        logger.warning("Twilio credentials not set, falling back to print")
        print(f"[SMS] To {phone}: {message}")
        return {"success": True, "message_id": None, "error": None}

    twilio_from = os.getenv("TWILIO_FROM_NUMBER", "")
    try:
        resp = httpx.post(
            f"{TWILIO_API_BASE}/{account_sid}/Messages.json",
            data={"From": twilio_from, "To": phone, "Body": message},
            auth=(account_sid, auth_token),
            timeout=15.0,
        )
        if resp.is_success:
            data = resp.json()
            return {"success": True, "message_id": data.get("sid"), "error": None}
        error_msg = f"Twilio API error {resp.status_code}: {resp.text}"
        logger.error(error_msg)
        return {"success": False, "message_id": None, "error": error_msg}
    except httpx.TimeoutException:
        logger.error("Twilio API request timed out")
        return {"success": False, "message_id": None, "error": "Request timed out"}
    except Exception as exc:
        logger.error("Twilio API request failed: %s", exc)
        return {"success": False, "message_id": None, "error": str(exc)}


def send_notification(
    notification_type: str,
    recipient: str,
    subject: str,
    body: str,
    **kwargs,
) -> dict:
    if notification_type == NOTIFICATION_TYPES["email"]:
        return send_email(recipient, subject, body, html_body=kwargs.get("html_body"))
    if notification_type == NOTIFICATION_TYPES["push"]:
        return send_push_notification(recipient, subject, body, data=kwargs.get("data"))
    if notification_type == NOTIFICATION_TYPES["sms"]:
        return send_sms(recipient, body)
    error_msg = f"Unknown notification type: {notification_type}"
    logger.error(error_msg)
    return {"success": False, "message_id": None, "error": error_msg}


def send_email_notification(email: str, subject: str, body: str) -> dict:
    return send_email(email, subject, body)


def send_sms_notification(phone: str, message: str) -> dict:
    return send_sms(phone, message)


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
