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
from database.schemas.orchestrator import PlanRequest

router = APIRouter()


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


@router.post("/plan", summary="Break down a complex query into a plan", status_code=200)
async def create_plan(query_data: PlanRequest, current_user=Depends(get_current_user)):
    try:
        result = await orchestrate_plan(current_user.user.id, query_data.query, query_data.context)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error("Planner failed", error=str(e))
        return {
            "status": "success",
            "data": {
                "plan_id": "fallback",
                "steps": [{"action": "search", "target": "all", "reasoning": "Fallback plan", "confidence": 0.5}],
                "summary": "Search across all modules",
            },
        }


@router.post("/execute", summary="Execute an action", status_code=200)
async def create_execution(query_data: PlanRequest, current_user=Depends(get_current_user)):
    try:
        result = await orchestrate_execute(current_user.user.id, query_data.query, query_data.context)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error("Executor failed", error=str(e))
        return {"status": "success", "data": {"action": "noop", "result": {}, "summary": "No action taken"}}


@router.post("/trigger/cleanup", status_code=201, summary="Run data retention cleanup")
async def trigger_data_cleanup(
    request: Request,
    audit_days: int = 90,
    chat_days: int = 90,
    notification_days: int = 30,
    current_user=Depends(get_current_user),
):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await run_data_retention_cleanup(audit_days, chat_days, notification_days)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
