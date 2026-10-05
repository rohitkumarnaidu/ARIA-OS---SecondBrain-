from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from shared.utils.rate_limiter import endpoint_limiter
from shared.utils.retention import run_data_retention_cleanup
from shared.utils.logger import logger
from config.core.auth import get_current_user
from ai.agents.briefing_agent import generate_daily_briefing
from ai.agents.opportunity_agent import run_opportunity_radar
from ai.agents.weekly_review_agent import generate_weekly_review
from ai.agents.sleep_agent import analyze_sleep, suggest_bedtime
from ai.agents.nudge_agent import run_all_nudges
from ai.orchestrator import orchestrate_plan, execute_action as orchestrate_execute
from ai.orchestrator_core import (
    MAX_AGENTS_PER_PLAN,
    execute as orchestrator_execute_plan,
    plan as build_orchestration_plan,
    synthesize as synthesize_orchestration,
)
from database.schemas.orchestrator import PlanRequest

router = APIRouter()

# Actions `/execute` will perform. The action name arrives in `context`, which is
# entirely client-supplied, and was previously never validated. It was also
# inferred from `query.startswith("delete ")`, so any free text beginning
# "delete " -- "delete my bank details", "delete last week's notes" -- resolved
# to `delete_task` and issued a DELETE against `tasks`.
ALLOWED_ACTIONS = frozenset(
    {
        "create_task",
        "update_task",
        "complete_task",
        "create_habit_log",
        "delete_task",
    }
)

# Destructive actions additionally require the caller to say so explicitly.
# A read can reasonably be inferred; a delete cannot.
CONFIRMATION_REQUIRED_ACTIONS = frozenset({"delete_task"})


@router.post("/trigger/briefing", summary="Trigger daily briefing", status_code=201)
async def trigger_briefing(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await generate_daily_briefing(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/radar", summary="Trigger opportunity radar", status_code=201)
async def trigger_radar(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        opportunities = await run_opportunity_radar(current_user.user.id)
        return {"status": "success", "count": len(opportunities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/weekly-review", summary="Trigger weekly review", status_code=201)
async def trigger_weekly_review(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        review = await generate_weekly_review(current_user.user.id)
        return {"status": "success", "data": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/sleep-analysis", summary="Trigger sleep analysis", status_code=201)
async def trigger_sleep_analysis(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await analyze_sleep(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/sleep-bedtime", summary="Suggest optimal bedtime", status_code=201)
async def trigger_sleep_bedtime(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await suggest_bedtime(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/nudges", summary="Trigger proactive nudges", status_code=201)
async def trigger_nudges(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await run_all_nudges(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _plan_as_frontend_steps(plan_obj: Any) -> list:
    """Render an `OrchestrationPlan` in the shape the /agents page renders.

    The frontend's `AgentTask` is `{id, name, description, status, dependsOn,
    confirmationRequired}`. It used to be synthesised from a hardcoded five-entry
    list in `apps/web/lib/ai/orchestrator.ts` naming four endpoints with no agent
    behind them. It now comes from the real registry, so the page lists the
    agents that will actually run.
    """
    from ai.registry import get_agent as lookup_agent

    steps = []
    for step in plan_obj.steps:
        spec = lookup_agent(step.agent_id)
        steps.append(
            {
                "id": step.agent_id,
                "name": step.name,
                "description": spec.description if spec else step.reason,
                "status": "waiting_confirmation" if step.hitl_required else "pending",
                "dependsOn": list(step.depends_on),
                "confirmationRequired": step.hitl_required,
                "confidence": plan_obj.confidence,
                "mutates": step.mutates,
            }
        )
    return steps


@router.post("/plan", summary="Break down a complex query into a plan", status_code=200)
async def create_plan(query_data: PlanRequest, current_user=Depends(get_current_user)):
    """Return the legacy planner's plan plus a real, registry-backed agent list.

    `orchestrate_plan` is still called first: its `plan_id`/`steps`/`summary` are
    the documented `PlanResponse` contract and several consumers read them. The
    `agents[]` array is additive and comes from `ai.orchestrator_core.plan`,
    which classifies the query and selects real agents from `ai.registry`. That
    is what replaced the hardcoded agent list on the frontend.
    """
    legacy = None
    try:
        legacy = await orchestrate_plan(current_user.user.id, query_data.query, query_data.context)
    except Exception as e:
        logger.error("Legacy planner failed; continuing with the registry plan", error=str(e))

    registry_plan = None
    try:
        registry_plan = await build_orchestration_plan(current_user.user.id, query_data.query)
    except Exception as e:
        logger.error("Registry planner failed", error=str(e))

    if legacy is None:
        legacy = {
            "plan_id": "fallback",
            "steps": [{"action": "search", "target": "all", "reasoning": "Fallback plan", "confidence": 0.5}],
            "summary": "Search across all modules",
        }

    data: Dict[str, Any] = dict(legacy)
    if registry_plan is not None:
        data.update(
            {
                "intent": registry_plan.intent,
                "confidence": registry_plan.confidence,
                "agents": _plan_as_frontend_steps(registry_plan),
                "entities": registry_plan.entities,
            }
        )
    else:
        data.setdefault("agents", [])
        data.setdefault("intent", "general")
        data.setdefault("confidence", 0.0)

    return {"status": "success", "data": data}


@router.post("/execute", summary="Execute an action", status_code=200)
async def create_execution(query_data: PlanRequest, current_user=Depends(get_current_user)):
    """Run the requested action, then attach the orchestrator's real plan.

    **Security.** The action name comes from `context`, which is client-supplied
    and was never validated. It is now checked against `ALLOWED_ACTIONS`, and a
    destructive action additionally requires `context.confirmed`.

    **Orchestration.** After the action runs, the message is planned against the
    real agent registry and executed. `action`, `result` and `summary` keep their
    previous meaning; `result.agents`, `result.steps` and `result.response` are
    additive and are what the /agents page renders.
    """
    context: Dict[str, Any] = dict(query_data.context or {})
    requested_action: Optional[str] = context.get("action")

    if requested_action is not None and requested_action not in ALLOWED_ACTIONS:
        logger.warn(
            "Rejected action outside the allow-list",
            action=requested_action,
            user_id=current_user.user.id,
        )
        return {
            "status": "success",
            "data": {
                "action": "rejected",
                "result": {},
                "summary": (
                    f"Action {requested_action!r} is not permitted. "
                    f"Allowed actions: {', '.join(sorted(ALLOWED_ACTIONS))}."
                ),
            },
        }

    if requested_action in CONFIRMATION_REQUIRED_ACTIONS and not context.get("confirmed"):
        return {
            "status": "success",
            "data": {
                "action": "awaiting_confirmation",
                "result": {},
                "summary": (
                    f"{requested_action} is destructive and requires explicit "
                    "confirmation. Re-send with context.confirmed = true."
                ),
            },
        }

    try:
        result = dict(await orchestrate_execute(current_user.user.id, query_data.query, context))
    except Exception as e:
        logger.error("Executor failed", error=str(e))
        return {"status": "success", "data": {"action": "noop", "result": {}, "summary": "No action taken"}}

    # Orchestration is strictly additive: a failure here leaves the action result
    # untouched rather than turning a successful action into an error.
    if result.get("action") in {"rejected", "noop", "awaiting_confirmation"}:
        return {"status": "success", "data": result}

    try:
        registry_plan = await build_orchestration_plan(current_user.user.id, query_data.query)
        capped = registry_plan.model_copy(update={"steps": registry_plan.steps[:MAX_AGENTS_PER_PLAN]})
        execution = await orchestrator_execute_plan(capped, current_user.user.id)
        reply = await synthesize_orchestration(execution.results, query_data.query)
        payload = result.get("result")
        payload = dict(payload) if isinstance(payload, dict) else {}
        payload.update(
            {
                "plan_id": registry_plan.plan_id,
                "intent": registry_plan.intent,
                "confidence": registry_plan.confidence,
                "agents": _plan_as_frontend_steps(registry_plan),
                "steps": [
                    {
                        "agent_id": r.agent_id,
                        "status": r.status,
                        "error": r.error,
                        "used_fallback": r.used_fallback,
                        "duration_ms": r.duration_ms,
                    }
                    for r in execution.results
                ],
                "response": reply,
            }
        )
        result["result"] = payload
    except Exception as e:
        logger.warn("Orchestration enrichment failed; returning the action result alone", error=str(e))

    return {"status": "success", "data": result}


@router.post("/trigger/cleanup", status_code=201, summary="Run data retention cleanup")
async def trigger_data_cleanup(
    request: Request,
    audit_days: int = 90,
    chat_days: int = 90,
    notification_days: int = 30,
    current_user=Depends(get_current_user),
):
    """Prune this user's own expired rows.

    Previously called `run_data_retention_cleanup` with no scope at all, which
    issued an unscoped DELETE against `audit_logs`, `chat_messages` and
    `notifications`. Any authenticated user could therefore destroy every other
    user's rows past the cutoff. Now scoped to `current_user.user.id`.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await run_data_retention_cleanup(audit_days, chat_days, notification_days, current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
