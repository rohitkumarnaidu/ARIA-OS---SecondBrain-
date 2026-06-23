from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def log_audit(
    user_id: str,
    action: str,
    resource: str,
    resource_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    try:
        supabase = get_supabase_client()
        supabase.from_("audit_logs").insert({
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }).execute()
    except Exception as e:
        logger.error("Failed to write audit log", error=str(e), action=action, resource=resource)


CREATE_ACTIONS = {"POST"}
UPDATE_ACTIONS = {"PUT", "PATCH"}
DELETE_ACTIONS = {"DELETE"}

MUTATION_METHODS = CREATE_ACTIONS | UPDATE_ACTIONS | DELETE_ACTIONS


def action_from_method(method: str) -> str:
    if method in CREATE_ACTIONS:
        return "create"
    if method in UPDATE_ACTIONS:
        return "update"
    if method in DELETE_ACTIONS:
        return "delete"
    return "read"


async def audit_middleware_dispatch(
    request,
    response,
    user_id: str | None = None,
    duration_ms: float = 0,
):
    if request.method not in MUTATION_METHODS:
        return
    if not user_id:
        return

    resource = str(request.url.path).replace("/api/v1/", "").split("/")[0]
    await log_audit(
        user_id=user_id,
        action=action_from_method(request.method),
        resource=resource,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
