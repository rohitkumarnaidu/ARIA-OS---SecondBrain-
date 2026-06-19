from fastapi import APIRouter, Depends, HTTPException, Request
from shared.utils.rate_limiter import endpoint_limiter
from config.core.auth import get_current_user
from ai.agents.briefing_agent import generate_daily_briefing
from ai.agents.opportunity_agent import run_opportunity_radar
from ai.agents.weekly_review_agent import generate_weekly_review
from ai.agents.sleep_agent import analyze_sleep, suggest_bedtime
from ai.agents.nudge_agent import run_all_nudges

router = APIRouter()


@router.post("/trigger/briefing", status_code=201)
async def trigger_briefing(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await generate_daily_briefing(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/radar", status_code=201)
async def trigger_radar(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        opportunities = await run_opportunity_radar(current_user.user.id)
        return {"status": "success", "count": len(opportunities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/weekly-review", status_code=201)
async def trigger_weekly_review(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        review = await generate_weekly_review(current_user.user.id)
        return {"status": "success", "data": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/sleep-analysis", status_code=201)
async def trigger_sleep_analysis(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await analyze_sleep(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/sleep-bedtime", status_code=201)
async def trigger_sleep_bedtime(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await suggest_bedtime(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/nudges", status_code=201)
async def trigger_nudges(request: Request, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/automation"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    try:
        result = await run_all_nudges(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
