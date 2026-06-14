from fastapi import APIRouter, Depends
from config.core.auth import get_current_user
from ai.agents.briefing_agent import generate_daily_briefing
from ai.agents.opportunity_agent import run_opportunity_radar
from ai.agents.weekly_review_agent import generate_weekly_review
from ai.agents.sleep_agent import analyze_sleep, suggest_bedtime
from ai.agents.nudge_agent import run_all_nudges

router = APIRouter()


@router.post("/trigger/briefing")
async def trigger_briefing(current_user=Depends(get_current_user)):
    try:
        result = await generate_daily_briefing(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/radar")
async def trigger_radar(current_user=Depends(get_current_user)):
    try:
        opportunities = await run_opportunity_radar(current_user.user.id)
        return {"status": "success", "count": len(opportunities)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/weekly-review")
async def trigger_weekly_review(current_user=Depends(get_current_user)):
    try:
        review = await generate_weekly_review(current_user.user.id)
        return {"status": "success", "data": review}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/sleep-analysis")
async def trigger_sleep_analysis(current_user=Depends(get_current_user)):
    try:
        result = await analyze_sleep(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/sleep-bedtime")
async def trigger_sleep_bedtime(current_user=Depends(get_current_user)):
    try:
        result = await suggest_bedtime(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/trigger/nudges")
async def trigger_nudges(current_user=Depends(get_current_user)):
    try:
        result = await run_all_nudges(current_user.user.id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
