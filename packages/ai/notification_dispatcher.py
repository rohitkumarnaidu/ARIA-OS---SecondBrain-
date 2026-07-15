from typing import Optional, Dict, List
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from shared.utils.notifications import send_email, send_push_notification


class NotificationDispatcher:

    def send_push(self, user_id: str, title: str, body: str, data: Optional[Dict] = None) -> bool:
        try:
            result = send_push_notification(user_id, title, body, data)
            success = result.get("success", False)
            if success:
                logger.info("Push notification sent", user_id=user_id, title=title)
            else:
                logger.warn("Push notification failed", user_id=user_id, title=title, error=result.get("error"))
            return success
        except Exception as e:
            logger.error("Push notification error", user_id=user_id, title=title, error=str(e))
            return False

    def send_email(self, user_id: str, subject: str, body: str) -> bool:
        try:
            supabase = get_supabase_client()
            user_resp = supabase.from_("users").select("email").eq("id", user_id).execute()
            email = user_resp.data[0].get("email") if user_resp.data else None
            if not email:
                logger.warn("Cannot send email: user has no email", user_id=user_id)
                return False
            result = send_email(email, subject, body)
            success = result.get("success", False)
            if success:
                logger.info("Email sent", user_id=user_id, subject=subject)
            else:
                logger.warn("Email send failed", user_id=user_id, subject=subject, error=result.get("error"))
            return success
        except Exception as e:
            logger.error("Email send error", user_id=user_id, subject=subject, error=str(e))
            return False

    def send_in_app(self, user_id: str, title: str, body: str, type: str = "info") -> bool:
        try:
            supabase = get_supabase_client()
            data = {
                "user_id": user_id,
                "title": title,
                "body": body,
                "type": type,
                "read": False,
            }
            result = supabase.from_("notifications").insert(data).execute()
            success = bool(result.data)
            if success:
                logger.info("In-app notification created", user_id=user_id, title=title)
            return success
        except Exception as e:
            logger.error("In-app notification error", user_id=user_id, title=title, error=str(e))
            return False

    def dispatch_to_all(self, user_id: str, title: str, body: str, channels: List[str]) -> Dict[str, bool]:
        results = {}
        for channel in channels:
            if channel == "push":
                results["push"] = self.send_push(user_id, title, body)
            elif channel == "email":
                results["email"] = self.send_email(user_id, title, body)
            elif channel == "in_app":
                results["in_app"] = self.send_in_app(user_id, title, body)
            else:
                logger.warn("Unknown notification channel", channel=channel)
                results[channel] = False
        return results


dispatcher = NotificationDispatcher()
